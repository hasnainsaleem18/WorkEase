"""
Message Processing Pipeline Demo

Demonstrates the complete workflow:
1. Mock messages arrive from Gmail/Slack agents

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_client import MockLLMClient, OllamaLLMClient
from core.orchestrator import Message, MessageSource, Orchestrator
from database.memory import MemoryStore


class Colors:
    """ANSI color codes for pretty terminal output"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


async def demo_with_mock_llm():
    """
    Demo using mock LLM (no Ollama installation required).
    Fast and simple for testing the pipeline.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(
        f"{Colors.HEADER}{Colors.BOLD}WorkEase Message Processing Pipeline Demo{Colors.END}"
    )
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}\n")

    print(f"{Colors.CYAN}🔧 Initializing Mock LLM (no Ollama needed)...{Colors.END}")
    llm = MockLLMClient()
    await llm.initialize()
    print(f"{Colors.GREEN}✓ Mock LLM ready{Colors.END}\n")

    # Initialize orchestrator
    print(f"{Colors.CYAN}🎯 Initializing Orchestrator...{Colors.END}")
    orchestrator = Orchestrator(llm)
    print(f"{Colors.GREEN}✓ Orchestrator ready{Colors.END}\n")

    # Create mock messages (simulating what Gmail/Slack agents would provide)
    mock_messages = [
        Message(
            id="gmail_001",
            source=MessageSource.GMAIL,
            sender="boss@company.com",
            subject="Q4 Report Due Tomorrow",
            content="Hi team, we need the quarterly report completed and sent to me by end of day today. Please include all Q4 metrics, budget analysis, and future projections. This is urgent for tomorrow's board meeting.",
        ),
        Message(
            id="slack_001",
            source=MessageSource.SLACK,
            sender="alice@team.slack",
            subject=None,
            content="Hey everyone, don't forget to update the project board with today's progress. Also, please review the PR I opened this morning - need approval before EOD.",
        ),
        Message(
            id="gmail_002",
            source=MessageSource.GMAIL,
            sender="client@example.com",
            subject="Re: Project Update",
            content="Thanks for the update. Everything looks good. No action needed from our side right now. We'll reach out if we have questions.",
        ),
        Message(
            id="slack_002",
            source=MessageSource.SLACK,
            sender="john@team.slack",
            subject=None,
            content="Meeting scheduled for 3pm today to discuss the new feature. Please come prepared with your status updates.",
        ),
    ]

    print(
        f"{Colors.YELLOW}📬 Processing {len(mock_messages)} messages...{Colors.END}\n"
    )

    # Process each message
    for i, message in enumerate(mock_messages, 1):
        print(f"{Colors.BOLD}{'─' * 70}{Colors.END}")
        print(
            f"{Colors.BLUE}{Colors.BOLD}Message {i}/{len(mock_messages)}: {message.source.value.upper()}{Colors.END}"
        )
        print(f"{Colors.BOLD}{'─' * 70}{Colors.END}\n")

        print(f"  📧 From: {Colors.BOLD}{message.sender}{Colors.END}")
        if message.subject:
            print(f"  📋 Subject: {Colors.BOLD}{message.subject}{Colors.END}")
        print(f"  📝 Content:\n     {message.content[:150]}...")
        print()

        # Process through orchestrator
        result = await orchestrator.process_message(message)

        # Display summary
        summary = result["summary"]
        print(f"  {Colors.GREEN}🤖 AI SUMMARY:{Colors.END}")
        print(f"     {summary.summary}")
        print()

        if summary.key_points:
            print(f"  {Colors.CYAN}📌 KEY POINTS:{Colors.END}")
            for point in summary.key_points:
                print(f"     • {point}")
            print()

        print(f"  {Colors.YELLOW}📊 ANALYSIS:{Colors.END}")
        print(f"     Sentiment: {summary.sentiment}")
        print(f"     Urgency: {summary.urgency_level}/10")
        print()

        # Display extracted tasks
        tasks = result["tasks"]
        if tasks:
            print(f"  {Colors.GREEN}✅ EXTRACTED TASKS ({len(tasks)}):{Colors.END}")
            for idx, task in enumerate(tasks, 1):
                priority_color = (
                    Colors.RED
                    if task.priority >= 8
                    else Colors.YELLOW
                    if task.priority >= 5
                    else Colors.CYAN
                )
                print(
                    f"     {idx}. {task.description} {priority_color}[Priority: {task.priority}/10]{Colors.END}"
                )
                if task.deadline:
                    print(f"        ⏰ Deadline: {task.deadline}")
        else:
            print(f"  {Colors.CYAN}ℹ️  No actionable tasks identified{Colors.END}")

        print()

    print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(
        f"{Colors.GREEN}{Colors.BOLD}✓ All messages processed successfully!{Colors.END}"
    )
    print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 70}{Colors.END}\n")

    # Show stats
    stats = orchestrator.get_stats()
    print(f"{Colors.CYAN}📈 Processing Statistics:{Colors.END}")
    print(f"   Total tasks extracted: {stats['tasks_extracted_count']}")
    print(f"   LLM connected: {stats['llm_connected']}")
    print()


async def demo_with_ollama():
    """
    Demo using real Ollama LLM (requires Ollama installation).
    Provides actual AI reasoning and analysis.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}WorkEase with Real Ollama LLM{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}\n")

    print(f"{Colors.CYAN}🔧 Initializing Ollama LLM...{Colors.END}")
    print(
        f"{Colors.YELLOW}   Note: This requires Ollama to be running on localhost:11434{Colors.END}"
    )
    print(
        f"{Colors.YELLOW}   Install with: curl -fsSL https://ollama.com/install.sh | sh{Colors.END}\n"
    )

    llm = OllamaLLMClient(model="llama3.2:3b")

    try:
        await llm.initialize()
        print(
            f"{Colors.GREEN}✓ Ollama LLM connected (model: llama3.2:3b){Colors.END}\n"
        )
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to connect to Ollama: {e}{Colors.END}")
        print(f"\n{Colors.YELLOW}Falling back to Mock LLM...{Colors.END}\n")
        await demo_with_mock_llm()
        return

    # Initialize orchestrator with real LLM
    orchestrator = Orchestrator(llm)

    # Use same mock messages
    message = Message(
        id="gmail_001",
        source=MessageSource.GMAIL,
        sender="boss@company.com",
        subject="Urgent: Project Deadline",
        content="Hi, we need to finalize the project proposal by Friday. Please prepare the technical architecture document and cost estimates. This is critical for the client meeting next week.",
    )

    print(f"{Colors.BLUE}{Colors.BOLD}Processing message with real AI...{Colors.END}\n")
    print(f"  From: {message.sender}")
    print(f"  Subject: {message.subject}")
    print(f"  Content: {message.content}")
    print()

    result = await orchestrator.process_message(message)

    summary = result["summary"]
    print(f"{Colors.GREEN}🤖 AI-Generated Summary:{Colors.END}")
    print(f"   {summary.summary}\n")

    tasks = result["tasks"]
    if tasks:
        print(f"{Colors.GREEN}✅ Tasks Extracted by AI:{Colors.END}")
        for i, task in enumerate(tasks, 1):
            print(f"   {i}. {task.description} [Priority: {task.priority}/10]")

    await llm.close()
    print(f"\n{Colors.GREEN}✓ Demo complete!{Colors.END}\n")


async def demo_with_database():
    """
    Demo showing full pipeline including database persistence.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}WorkEase with Database Persistence{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}\n")

    # Initialize components
    print(f"{Colors.CYAN}🔧 Initializing components...{Colors.END}")

    llm = MockLLMClient()
    await llm.initialize()

    memory = MemoryStore(db_path="examples/demo.db")
    await memory.initialize()

    orchestrator = Orchestrator(llm, context_provider=memory)

    print(f"{Colors.GREEN}✓ All components ready{Colors.END}\n")

    # Process a message
    message = Message(
        id="test_msg_001",
        source=MessageSource.GMAIL,
        sender="test@example.com",
        subject="Test Message",
        content="Please review the document and send feedback by tomorrow. This is important for the project timeline.",
    )

    print(f"{Colors.BLUE}Processing and storing message...{Colors.END}\n")

    # Process
    result = await orchestrator.process_message(message)

    # Store in database
    await memory.store_message(
        message_id=message.id,
        source=message.source.value,
        sender=message.sender,
        content=message.content,
        subject=message.subject,
    )

    summary = result["summary"]
    summary_id = await memory.store_summary(
        message_id=message.id, summary=summary.summary, model_used="mock_llm"
    )

    tasks = result["tasks"]
    task_texts = [t.description for t in tasks]
    priorities = [t.priority for t in tasks]
    await memory.store_tasks(
        message_id=message.id,
        tasks=task_texts,
        summary_id=summary_id,
        priorities=priorities,
    )

    print(f"{Colors.GREEN}✓ Message stored in database{Colors.END}")
    print(f"{Colors.GREEN}✓ Summary stored (ID: {summary_id}){Colors.END}")
    print(f"{Colors.GREEN}✓ {len(tasks)} tasks stored{Colors.END}\n")

    # Retrieve from database
    print(f"{Colors.CYAN}📚 Retrieving from database...{Colors.END}\n")

    stored_message = await memory.get_message(message.id)
    print(f"  Message: {stored_message['sender']} - {stored_message['subject']}")

    stored_summary = await memory.get_summary(message.id)
    print(f"  Summary: {stored_summary}")

    stored_tasks = await memory.get_tasks(message.id)
    print(f"  Tasks: {len(stored_tasks)} stored")
    for task in stored_tasks:
        print(f"    - {task['task_text']} [Priority: {task['priority']}]")

    print()

    # Show all pending tasks
    all_pending = await memory.get_pending_tasks()
    print(
        f"{Colors.YELLOW}📋 All pending tasks in database: {len(all_pending)}{Colors.END}\n"
    )

    await memory.close()
    print(f"{Colors.GREEN}✓ Database closed{Colors.END}\n")


async def main():
    """Main entry point with menu selection"""
    print(f"\n{Colors.BOLD}WorkEase Backend Demo{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")

    print("Choose demo mode:\n")
    print(f"  {Colors.GREEN}1{Colors.END} - Mock LLM (fast, no installation required)")
    print(
        f"  {Colors.YELLOW}2{Colors.END} - Real Ollama LLM (requires Ollama installation)"
    )
    print(f"  {Colors.CYAN}3{Colors.END} - With Database Persistence")
    print(f"  {Colors.RED}0{Colors.END} - Exit\n")

    choice = input("Enter choice (default=1): ").strip() or "1"

    if choice == "1":
        await demo_with_mock_llm()
    elif choice == "2":
        await demo_with_ollama()
    elif choice == "3":
        await demo_with_database()
    elif choice == "0":
        print("Exiting...")
        return
    else:
        print(f"{Colors.RED}Invalid choice{Colors.END}")
        return

    print(f"\n{Colors.CYAN}💡 Next Steps:{Colors.END}")
    print("  • Implement Gmail Agent (agents/gmail_agent.py)")
    print("  • Implement Slack Agent (agents/slack_agent.py)")
    print("  • Replace Mock LLM with real Ollama")
    print("  • Connect orchestrator to event bus")
    print("  • Build PyQt6 UI to display results")
    print("  • Add voice interface (STT/TTS)")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback

        traceback.print_exc()
