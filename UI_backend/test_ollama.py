#!/usr/bin/env python3
"""
Test script to verify Ollama integration
"""
import sys
import os

# Add UI directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'UI'))

from ai_service import OllamaService

def test_ollama():
    print("Testing Ollama connection...")
    
    ollama = OllamaService(model_name="qwen3:0.6b")
    
    # Test connection
    if not ollama.check_connection():
        print("❌ Ollama is not running or not accessible")
        return False
    
    print("✅ Ollama is running")
    
    # Test summary generation
    print("\nTesting summary generation...")
    test_message = """
    Hey team, just wanted to remind everyone about the important meeting tomorrow at 2 PM.
    We'll be discussing the Q4 roadmap and need everyone's input on the new features.
    Please review the documents I sent earlier and come prepared with your thoughts.
    This is urgent as we need to finalize everything by end of week.
    """
    
    summary = ollama.generate_summary(
        message_text=test_message,
        sender="John Doe",
        subject="Q4 Meeting Reminder"
    )
    
    if summary:
        print(f"✅ Summary generated successfully:")
        print(f"   {summary}")
        return True
    else:
        print("❌ Failed to generate summary")
        return False

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)
