"""
Simple Message Processing Demo - No External Dependencies

This is a minimal demo that works with just Python standard library.
Shows the core concept of message → summary → task extraction pipeline.

Run: python examples/simple_demo.py
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Message:
    """Simple message representation"""

    id: str
    source: str  # 'gmail' or 'slack'
    sender: str
    content: str
    subject: Optional[str] = None


@dataclass
class Task:
    """Simple task representation"""

    description: str
    priority: int  # 1-10
    deadline: Optional[str] = None


class SimpleLLM:
    """
    Mock LLM that simulates AI processing.
    In real implementation, this would call Ollama or OpenAI API.
    """

    def summarize(self, message: Message) -> str:
        """Generate a simple summary based on keywords"""
        content_lower = message.content.lower()

        # Simple keyword-based summarization
        if (
            "report" in content_lower
            and "urgent" in content_lower
            or "eod" in content_lower
        ):
            return (
                f"{message.sender} requests urgent completion of report by end of day."
            )
        elif "meeting" in content_lower:
            return f"{message.sender} scheduled a meeting, review required."
        elif "update" in content_lower:
            return f"{message.sender} requests project updates."
        elif "thanks" in content_lower or "no action" in content_lower:
            return f"{message.sender} acknowledged, no action required."
        else:
            return f"{message.sender} sent a message requiring attention."

    def extract_tasks(self, message: Message) -> List[Task]:
        """Extract tasks from message using keyword matching"""
        content_lower = message.content.lower()
        tasks = []

        # Check for common task patterns
        if "report" in content_lower:
            priority = 9 if "urgent" in content_lower or "eod" in content_lower else 6
            tasks.append(
                Task(
                    description="Prepare and submit report",
                    priority=priority,
                    deadline="Today EOD"
                    if "eod" in content_lower or "today" in content_lower
                    else None,
                )
            )

        if "update" in content_lower and "board" in content_lower:
            tasks.append(
                Task(description="Update project board", priority=5, deadline=None)
            )

        if "review" in content_lower:
            tasks.append(
                Task(
                    description="Review document/PR",
                    priority=7 if "asap" in content_lower else 5,
                    deadline=None,
                )
            )

        if "meeting" in content_lower:
            tasks.append(
                Task(
                    description="Attend/prepare for meeting", priority=6, deadline=None
                )
            )

        return tasks


class SimpleOrchestrator:
    """
    Minimal orchestrator that processes messages.
    Real implementation would have LLM integration, event bus, database, etc.
    """

    def __init__(self, llm: SimpleLLM):
        self.llm = llm
        self.processed_count = 0

    def process_message(self, message: Message) -> dict:
        """Process a message through the pipeline"""
        # Step 1: Generate summary
        summary = self.llm.summarize(message)

        # Step 2: Extract tasks
        tasks = self.llm.extract_tasks(message)

        self.processed_count += 1

        return {
            "message_id": message.id,
            "summary": summary,
            "tasks": tasks,
            "processed_at": datetime.now().isoformat(),
        }


def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)


def print_header(text):
    """Print a formatted header"""
    print_separator()
    print(f"  {text}")
    print_separator()
    print()


def print_result(result: dict, message: Message):
    """Pretty print processing result"""
    print(f"📧 FROM: {message.sender}")
    if message.subject:
        print(f"📋 SUBJECT: {message.subject}")
    print(f"📝 CONTENT: {message.content[:100]}...")
    print()

    print(f"🤖 AI SUMMARY:")
    print(f"   {result['summary']}")
    print()

    tasks = result["tasks"]
    if tasks:
        print(f"✅ EXTRACTED TASKS ({len(tasks)}):")
        for i, task in enumerate(tasks, 1):
            priority_marker = (
                "🔴" if task.priority >= 8 else "🟡" if task.priority >= 5 else "🟢"
            )
            print(
                f"   {i}. {task.description} {priority_marker} [Priority: {task.priority}/10]"
            )
            if task.deadline:
                print(f"      ⏰ Deadline: {task.deadline}")
    else:
        print("ℹ️  No actionable tasks identified")
    print()


def main():
    """Run the demo"""
    print()
    print_header("AutoReturn Backend Demo - Message Processing Pipeline")

    print("This demo shows how AutoReturn processes messages:")
    print("  1. Receive message (from Gmail/Slack agent)")
    print("  2. Generate AI summary")
    print("  3. Extract actionable tasks")
    print()

    # Initialize components
    print("🔧 Initializing components...")
    llm = SimpleLLM()
    orchestrator = SimpleOrchestrator(llm)
    print("✓ Mock LLM ready")
    print("✓ Orchestrator ready")
    print()

    # Create sample messages
    messages = [
        Message(
            id="gmail_001",
            source="gmail",
            sender="boss@company.com",
            subject="Q4 Report Due Tomorrow",
            content="Hi team, we need the quarterly report completed and sent to me by end of day today. Please include all Q4 metrics, budget analysis, and future projections. This is urgent for tomorrow's board meeting.",
        ),
        Message(
            id="slack_001",
            source="slack",
            sender="alice@team.slack",
            content="Hey everyone, don't forget to update the project board with today's progress. Also, please review the PR I opened this morning - need approval before EOD.",
        ),
        Message(
            id="gmail_002",
            source="gmail",
            sender="client@example.com",
            subject="Re: Project Update",
            content="Thanks for the update. Everything looks good. No action needed from our side right now. We'll reach out if we have questions.",
        ),
        Message(
            id="slack_002",
            source="slack",
            sender="john@team.slack",
            content="Meeting scheduled for 3pm today to discuss the new feature. Please come prepared with your status updates.",
        ),
    ]

    print(f"📬 Processing {len(messages)} messages...")
    print()

    # Process each message
    for i, message in enumerate(messages, 1):
        print(f"━━━ Message {i}/{len(messages)}: {message.source.upper()} ━━━")
        print()

        result = orchestrator.process_message(message)
        print_result(result, message)

    print_separator()
    print(f"✓ Successfully processed {orchestrator.processed_count} messages!")
    print_separator()
    print()

    print("💡 NEXT STEPS (Not Implemented Yet):")
    print("   • Integrate real Gmail/Slack agents")
    print("   • Replace SimpleLLM with Ollama (local) or OpenAI (cloud)")
    print("   • Add database persistence (SQLite)")
    print("   • Connect to PyQt6 UI")
    print("   • Implement event bus for component communication")
    print("   • Add voice interface (wake word, STT, TTS)")
    print()

    print("📚 For full feature demo with real LLM:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Install Ollama
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
