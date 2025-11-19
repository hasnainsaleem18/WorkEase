"""
MIND-Model Core Implementation

Core classes for the Mesh Integration Networked Development Model.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class NodeState(str, Enum):
    """Node lifecycle states."""

    INACTIVE = "inactive"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Transition:
    """Represents a transition between nodes."""

    from_node: str
    to_node: str
    reason: str
    timestamp: datetime
    duration_seconds: float
    outcome: str  # "success", "failed", "partial"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeMetrics:
    """Metrics for a node."""

    entry_count: int = 0
    total_duration: float = 0.0
    output_quality: float = 0.0
    connection_usage: dict[str, int] = field(default_factory=dict)
    bottleneck_score: float = 0.0


class Node:
    """
    Base class for MIND-Model nodes.

    Each node represents a phase in the development lifecycle.
    """

    def __init__(
        self,
        name: str,
        symbol: str,
        connections: list[str],
        exit_criteria: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize node.

        Args:
            name: Node name
            symbol: Short symbol (e.g., "R", "D", "C")
            connections: List of connected node names
            exit_criteria: Criteria for completing this node
        """
        self.name = name
        self.symbol = symbol
        self.connections = connections
        self.exit_criteria = exit_criteria or {}
        self.state = NodeState.INACTIVE
        self.metrics = NodeMetrics()
        self.activation_time: Optional[float] = None
        self.outputs: dict[str, Any] = {}

    def activate(self) -> None:
        """Activate this node."""
        if self.state == NodeState.INACTIVE:
            self.state = NodeState.PENDING
            logger.info(f"Node {self.name} ({self.symbol}) activated")

    def start(self) -> None:
        """Start working on this node."""
        if self.state == NodeState.PENDING:
            self.state = NodeState.ACTIVE
            self.activation_time = time.time()
            self.metrics.entry_count += 1
            logger.info(f"Node {self.name} ({self.symbol}) started")

    def complete(self, outputs: dict[str, Any]) -> bool:
        """
        Complete this node.

        Args:
            outputs: Node outputs

        Returns:
            True if exit criteria met
        """
        if self.state != NodeState.ACTIVE:
            return False

        # Check exit criteria
        if not self._check_exit_criteria(outputs):
            logger.warning(f"Node {self.name} exit criteria not met")
            return False

        # Update metrics
        if self.activation_time:
            duration = time.time() - self.activation_time
            self.metrics.total_duration += duration

        self.outputs = outputs
        self.state = NodeState.COMPLETED
        logger.info(f"Node {self.name} ({self.symbol}) completed")
        return True

    def archive(self) -> None:
        """Archive this node."""
        if self.state == NodeState.COMPLETED:
            self.state = NodeState.ARCHIVED
            logger.info(f"Node {self.name} ({self.symbol}) archived")

    def reactivate(self) -> None:
        """Reactivate a completed node."""
        if self.state in [NodeState.COMPLETED, NodeState.ARCHIVED]:
            self.state = NodeState.PENDING
            logger.info(f"Node {self.name} ({self.symbol}) reactivated")

    def _check_exit_criteria(self, outputs: dict[str, Any]) -> bool:
        """
        Check if exit criteria are met.

        Args:
            outputs: Node outputs

        Returns:
            True if criteria met
        """
        for key, threshold in self.exit_criteria.items():
            if key not in outputs:
                return False
            if isinstance(threshold, (int, float)):
                if outputs[key] < threshold:
                    return False
            elif isinstance(threshold, bool):
                if outputs[key] != threshold:
                    return False
        return True

    def can_transition_to(self, target_node: str) -> bool:
        """
        Check if can transition to target node.

        Args:
            target_node: Target node name

        Returns:
            True if transition allowed
        """
        return target_node in self.connections

    def get_metrics(self) -> dict[str, Any]:
        """
        Get node metrics.

        Returns:
            Dictionary of metrics
        """
        avg_duration = (
            self.metrics.total_duration / self.metrics.entry_count
            if self.metrics.entry_count > 0
            else 0
        )

        return {
            "name": self.name,
            "symbol": self.symbol,
            "state": self.state.value,
            "entry_count": self.metrics.entry_count,
            "total_duration": self.metrics.total_duration,
            "avg_duration": avg_duration,
            "output_quality": self.metrics.output_quality,
            "bottleneck_score": self.metrics.bottleneck_score,
        }


class MINDModel:
    """
    MIND-Model framework implementation.

    Manages nodes, transitions, and mesh workflow.
    """

    def __init__(self, tier: str = "standard") -> None:
        """
        Initialize MIND-Model.

        Args:
            tier: Tier level ("light", "standard", "enterprise")
        """
        self.tier = tier
        self.nodes: dict[str, Node] = {}
        self.transitions: list[Transition] = []
        self.current_node: Optional[str] = None
        self.active_nodes: set[str] = set()

    def register_node(self, node: Node) -> None:
        """
        Register a node.

        Args:
            node: Node to register
        """
        self.nodes[node.name] = node
        logger.info(f"Registered node: {node.name} ({node.symbol})")

    def transition(
        self,
        from_node: str,
        to_node: str,
        reason: str,
        outcome: str = "success",
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Transition between nodes.

        Args:
            from_node: Source node name
            to_node: Target node name
            reason: Reason for transition
            outcome: Transition outcome
            metadata: Additional metadata

        Returns:
            True if transition successful
        """
        # Validate nodes exist
        if from_node not in self.nodes or to_node not in self.nodes:
            logger.error(f"Invalid transition: {from_node} → {to_node}")
            return False

        source = self.nodes[from_node]
        target = self.nodes[to_node]

        # Check if transition allowed
        if not source.can_transition_to(to_node):
            logger.error(
                f"Transition not allowed: {from_node} → {to_node} "
                f"(not in connections: {source.connections})"
            )
            return False

        # Record transition
        start_time = datetime.now()
        duration = (
            time.time() - source.activation_time if source.activation_time else 0
        )

        transition = Transition(
            from_node=from_node,
            to_node=to_node,
            reason=reason,
            timestamp=start_time,
            duration_seconds=duration,
            outcome=outcome,
            metadata=metadata or {},
        )

        self.transitions.append(transition)

        # Update metrics
        source.metrics.connection_usage[to_node] = (
            source.metrics.connection_usage.get(to_node, 0) + 1
        )

        # Activate target node
        target.activate()
        target.start()

        # Update active nodes
        self.active_nodes.add(to_node)
        if from_node in self.active_nodes and source.state == NodeState.COMPLETED:
            self.active_nodes.remove(from_node)

        self.current_node = to_node

        logger.info(
            f"Transition: {from_node} → {to_node} ({reason}) [{outcome}]"
        )
        return True

    def get_mesh_status(self) -> dict[str, Any]:
        """
        Get current mesh status.

        Returns:
            Dictionary with mesh status
        """
        return {
            "tier": self.tier,
            "total_nodes": len(self.nodes),
            "active_nodes": list(self.active_nodes),
            "current_node": self.current_node,
            "total_transitions": len(self.transitions),
            "nodes": {name: node.get_metrics() for name, node in self.nodes.items()},
        }

    def get_path_log(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get transition path log.

        Args:
            limit: Maximum number of transitions

        Returns:
            List of transitions
        """
        return [
            {
                "from": t.from_node,
                "to": t.to_node,
                "reason": t.reason,
                "timestamp": t.timestamp.isoformat(),
                "duration": t.duration_seconds,
                "outcome": t.outcome,
            }
            for t in self.transitions[-limit:]
        ]

    def analyze_bottlenecks(self) -> list[dict[str, Any]]:
        """
        Analyze bottlenecks in the mesh.

        Returns:
            List of bottleneck nodes
        """
        bottlenecks = []

        for name, node in self.nodes.items():
            if node.metrics.entry_count == 0:
                continue

            avg_duration = (
                node.metrics.total_duration / node.metrics.entry_count
            )

            # Calculate bottleneck score
            # High if: long duration, many entries, low quality
            score = (
                avg_duration * node.metrics.entry_count * (1 - node.metrics.output_quality)
            )

            node.metrics.bottleneck_score = score

            if score > 10:  # Threshold
                bottlenecks.append(
                    {
                        "node": name,
                        "score": score,
                        "avg_duration": avg_duration,
                        "entry_count": node.metrics.entry_count,
                    }
                )

        return sorted(bottlenecks, key=lambda x: x["score"], reverse=True)

    def calculate_rework_rate(self) -> float:
        """
        Calculate rework rate (backward transitions).

        Returns:
            Rework rate as percentage
        """
        if not self.transitions:
            return 0.0

        # Define forward flow
        forward_flow = [
            "requirements",
            "design",
            "coding",
            "testing",
            "deployment",
            "maintenance",
        ]

        backward_count = 0
        for transition in self.transitions:
            from_idx = (
                forward_flow.index(transition.from_node)
                if transition.from_node in forward_flow
                else -1
            )
            to_idx = (
                forward_flow.index(transition.to_node)
                if transition.to_node in forward_flow
                else -1
            )

            if from_idx != -1 and to_idx != -1 and to_idx < from_idx:
                backward_count += 1

        return (backward_count / len(self.transitions)) * 100

    def get_parallel_factor(self) -> float:
        """
        Calculate average number of concurrent active nodes.

        Returns:
            Average parallel factor
        """
        if not self.transitions:
            return 0.0

        # Sample active nodes at each transition
        active_counts = []
        for _ in self.transitions:
            active_counts.append(len(self.active_nodes))

        return sum(active_counts) / len(active_counts) if active_counts else 0.0
