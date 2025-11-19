"""
Multi-Agent Coordinator - Complex Multi-Step Command Execution

Decomposes complex commands into sequential sub-tasks and coordinates
execution across multiple agents with state management.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from core.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class SubTask:
    """Individual sub-task in a multi-step command."""

    id: str
    action: str
    target: str  # Agent target
    parameters: dict[str, Any]
    depends_on: Optional[str] = None  # Previous sub-task ID
    status: str = "pending"  # "pending", "executing", "completed", "failed"
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class MultiStepCommand:
    """Multi-step command representation."""

    id: str
    original_command: str
    sub_tasks: list[SubTask] = field(default_factory=list)
    current_step: int = 0
    state: dict[str, Any] = field(default_factory=dict)  # Shared state between tasks
    status: str = "pending"  # "pending", "executing", "completed", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class MultiAgentCoordinator:
    """
    Coordinates execution of multi-step commands across agents.

    Handles command decomposition, sequential execution, state passing,
    and failure recovery.
    """

    def __init__(self, orchestrator: Any, event_bus: EventBus, llm: Any) -> None:
        """
        Initialize the coordinator.

        Args:
            orchestrator: Orchestrator instance for agent routing
            event_bus: Event bus for communication
            llm: Local LLM for command decomposition
        """
        self.orchestrator = orchestrator
        self.event_bus = event_bus
        self.llm = llm
        self.active_commands: dict[str, MultiStepCommand] = {}
        self.command_history: list[MultiStepCommand] = []

    async def execute_multi_step(self, command: str, context_id: str = "default") -> None:
        """
        Execute a multi-step command.

        Args:
            command: Natural language multi-step command
            context_id: Session identifier
        """
        try:
            logger.info(f"Executing multi-step command: {command}")

            # Create command object
            command_obj = MultiStepCommand(
                id=f"cmd_{datetime.now().timestamp()}",
                original_command=command,
                started_at=datetime.now(),
            )

            # Decompose into sub-tasks
            sub_tasks = await self._decompose_command(command)
            command_obj.sub_tasks = sub_tasks
            command_obj.status = "executing"

            # Store active command
            self.active_commands[command_obj.id] = command_obj

            # Execute sub-tasks sequentially
            for i, sub_task in enumerate(sub_tasks):
                command_obj.current_step = i
                sub_task.status = "executing"

                logger.info(
                    f"Executing sub-task {i + 1}/{len(sub_tasks)}: {sub_task.action} on {sub_task.target}"
                )

                # Execute sub-task
                result = await self._execute_sub_task(command_obj.id, sub_task)

                if result.get("success"):
                    sub_task.status = "completed"
                    sub_task.result = result.get("data")

                    # Store result in shared state for next task
                    command_obj.state[sub_task.id] = result.get("data")
                else:
                    # Sub-task failed
                    sub_task.status = "failed"
                    sub_task.error = result.get("error")
                    await self._handle_failure(command_obj.id, sub_task.error or "Unknown error")
                    return

            # All sub-tasks completed
            command_obj.status = "completed"
            command_obj.completed_at = datetime.now()

            # Report success
            await self._report_success(command_obj)

            # Move to history
            self.command_history.append(command_obj)
            del self.active_commands[command_obj.id]

        except Exception as e:
            logger.error(f"Error executing multi-step command: {e}", exc_info=True)
            await self.event_bus.emit(
                "orchestrator.error",
                {"error": f"Multi-step command failed: {str(e)}", "command": command},
            )

    async def _decompose_command(self, command: str) -> list[SubTask]:
        """
        Decompose a complex command into sub-tasks using LLM.

        Args:
            command: Natural language command

        Returns:
            List of SubTask objects
        """
        prompt = f"""Decompose this multi-step command into sequential sub-tasks.

Command: {command}

Return JSON array of sub-tasks with this format:
[
  {{"action": "fetch", "target": "gmail", "parameters": {{}}}},
  {{"action": "send", "target": "slack", "parameters": {{"channel": "...", "message": "..."}}}}
]

Sub-tasks:"""

        try:
            response = await self.llm.generate(prompt)

            # Parse JSON response
            import json

            json_start = response.find("[")
            json_end = response.rfind("]") + 1

            if json_start == -1:
                raise ValueError("No JSON array found in LLM response")

            json_str = response[json_start:json_end]
            sub_tasks_data = json.loads(json_str)

            # Create SubTask objects
            sub_tasks = []
            for i, task_data in enumerate(sub_tasks_data):
                sub_task = SubTask(
                    id=f"subtask_{i}",
                    action=task_data.get("action", "unknown"),
                    target=task_data.get("target", "unknown"),
                    parameters=task_data.get("parameters", {}),
                    depends_on=f"subtask_{i-1}" if i > 0 else None,
                )
                sub_tasks.append(sub_task)

            logger.info(f"Decomposed into {len(sub_tasks)} sub-tasks")
            return sub_tasks

        except Exception as e:
            logger.error(f"Error decomposing command: {e}", exc_info=True)
            # Fallback: treat as single task
            return [
                SubTask(
                    id="subtask_0",
                    action="unknown",
                    target="unknown",
                    parameters={"original_command": command},
                )
            ]

    async def _execute_sub_task(
        self, command_id: str, sub_task: SubTask
    ) -> dict[str, Any]:
        """
        Execute a single sub-task.

        Args:
            command_id: Parent command ID
            sub_task: Sub-task to execute

        Returns:
            Execution result
        """
        try:
            # Get shared state from previous tasks
            command = self.active_commands[command_id]
            previous_results = command.state

            # Inject previous results into parameters if needed
            if sub_task.depends_on and sub_task.depends_on in previous_results:
                sub_task.parameters["previous_result"] = previous_results[sub_task.depends_on]

            # Route to appropriate agent via orchestrator
            from core.orchestrator import Intent

            intent = Intent(
                action=sub_task.action,
                target=sub_task.target,
                parameters=sub_task.parameters,
                confidence=1.0,
                context_id=command_id,
                raw_input=f"{sub_task.action} on {sub_task.target}",
            )

            # Execute via orchestrator
            await self.orchestrator.route_to_agent(intent)

            # Wait for agent response (simplified - in real implementation, use event subscription)
            await asyncio.sleep(2)  # Simulate agent execution

            # Return success (in real implementation, capture actual agent response)
            return {"success": True, "data": {"status": "completed"}}

        except Exception as e:
            logger.error(f"Error executing sub-task: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _handle_failure(self, command_id: str, error: str) -> None:
        """
        Handle sub-task failure.

        Args:
            command_id: Command ID
            error: Error message
        """
        command = self.active_commands.get(command_id)
        if not command:
            return

        command.status = "failed"
        command.error = error
        command.completed_at = datetime.now()

        logger.error(f"Multi-step command failed: {error}")

        # Notify user
        await self.event_bus.emit(
            "ui.notification",
            {
                "title": "Command Failed",
                "body": f"Multi-step command failed at step {command.current_step + 1}: {error}",
                "priority": "high",
            },
        )

        await self.event_bus.emit(
            "voice.speak",
            {"text": f"Command failed: {error}", "priority": "high"},
        )

        # Move to history
        self.command_history.append(command)
        del self.active_commands[command_id]

    async def _report_success(self, command: MultiStepCommand) -> None:
        """
        Report successful command completion.

        Args:
            command: Completed command
        """
        duration = (
            (command.completed_at - command.started_at).total_seconds()
            if command.completed_at and command.started_at
            else 0
        )

        logger.info(
            f"Multi-step command completed: {len(command.sub_tasks)} tasks in {duration:.1f}s"
        )

        # Notify user
        await self.event_bus.emit(
            "ui.notification",
            {
                "title": "Command Completed",
                "body": f"Successfully completed {len(command.sub_tasks)} tasks",
                "priority": "normal",
            },
        )

        await self.event_bus.emit(
            "voice.speak",
            {"text": "Command completed successfully", "priority": "normal"},
        )

    def get_active_commands(self) -> list[MultiStepCommand]:
        """
        Get currently executing commands.

        Returns:
            List of active commands
        """
        return list(self.active_commands.values())

    def get_command_history(self, limit: int = 10) -> list[MultiStepCommand]:
        """
        Get command execution history.

        Args:
            limit: Maximum number of commands

        Returns:
            List of historical commands
        """
        return self.command_history[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """
        Get coordinator statistics.

        Returns:
            Dictionary with stats
        """
        total = len(self.command_history)
        completed = sum(1 for cmd in self.command_history if cmd.status == "completed")
        failed = sum(1 for cmd in self.command_history if cmd.status == "failed")

        return {
            "active_commands": len(self.active_commands),
            "total_executed": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
        }
