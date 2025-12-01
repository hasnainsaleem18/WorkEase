#!/usr/bin/env python3
"""
Demo script to add test messages and show AI summary generation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'UI'))

from ai_service import OllamaService
from datetime import datetime

def demo_ai_summaries():
    print("=" * 60)
    print("AI Summary Feature Demo")
    print("=" * 60)
    
    # Test messages
    test_messages = [
        {
            "sender": "Alice Johnson",
            "subject": "Project Update",
            "content": "Hi team, I wanted to give you a quick update on the Q4 project. We've completed the initial design phase and are now moving into development. The timeline looks good and we should be on track for the December deadline. Please review the attached documents and let me know if you have any questions or concerns."
        },
        {
            "sender": "Bob Smith",
            "subject": "Urgent: Server Issue",
            "content": "URGENT: The production server is experiencing high load and response times are degrading. We need to investigate this immediately. I've already started looking into it but need help from the DevOps team. This is affecting our customers so it's critical we resolve this ASAP."
        },
        {
            "sender": "Carol Davis",
            "subject": "Meeting Reminder",
            "content": "Just a friendly reminder that we have our weekly standup tomorrow at 10 AM. Please come prepared to discuss your progress, any blockers, and your plans for the upcoming week. Looking forward to seeing everyone there!"
        },
        {
            "sender": "David Lee",
            "subject": "Code Review Request",
            "content": "Hey, I've just pushed my changes for the new authentication feature. Could someone please review the PR when you get a chance? It's not super urgent but would be great to get feedback before the end of the week. Thanks!"
        }
    ]
    
    # Initialize Ollama
    ollama = OllamaService(model_name="qwen3:0.6b")
    
    # Check connection
    if not ollama.check_connection():
        print("\n❌ ERROR: Ollama is not running!")
        print("\nPlease start Ollama:")
        print("  ollama serve")
        return False
    
    print("\n✅ Ollama is running\n")
    print("Generating summaries for test messages...\n")
    
    # Generate summaries
    for i, msg in enumerate(test_messages, 1):
        print(f"Message {i}/{len(test_messages)}")
        print(f"From: {msg['sender']}")
        print(f"Subject: {msg['subject']}")
        print(f"Content: {msg['content'][:80]}...")
        print("\nGenerating summary...", end=" ", flush=True)
        
        summary = ollama.generate_summary(
            message_text=msg['content'],
            sender=msg['sender'],
            subject=msg['subject']
        )
        
        if summary:
            print("✅")
            print(f"Summary: {summary}")
        else:
            print("❌ Failed")
        
        print("-" * 60)
        print()
    
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nNow run the application to see AI summaries in action:")
    print("  ./run.sh")
    
    return True

if __name__ == "__main__":
    success = demo_ai_summaries()
    sys.exit(0 if success else 1)
