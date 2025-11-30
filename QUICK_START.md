# AutoReturn Backend - Quick Start Guide

## 🎯 What's Implemented

This backend implements the **message processing pipeline** feature:

1. **Messages arrive** from Gmail/Slack (agents stubbed, ready for API integration)
2. **Orchestrator receives** and coordinates processing
3. **LLM analyzes** and generates AI summary of each message
4. **LLM extracts** actionable tasks from message content
5. **Results stored** in database (optional)

## 📁 What Was Created

```

│   ├── models.py                  # Data models (Message, Task, etc.)
│   ├── llm_client.py              # LLM interface (Ollama/Mock)
│   ├── orchestrator.py            # Central coordinator
│   ├── langchain_orchestrator.py  # 🟡 Base for LangChain (foundation only)
│   └── memory/                    # Context providers
│       ├── context_provider.py    # ✅ Protocol interface
│       ├── langchain_memory.py    # 🟡 LangChain memory (foundation only)
│       └── rag_provider.py        # 🟡 RAG vector store (foundation only)
│
├── agents/                        # 🔶 STUBBED (interfaces ready)
│   ├── base_agent.py              # Agent protocol
│   ├── gmail_agent.py             # Gmail API stub
│   └── slack_agent.py             # Slack API stub
│
├── algorithms/                    # ✅ IMPLEMENTED
│   └── task_extractor.py          # Pattern-based task extraction
│
├── database/                      # ✅ IMPLEMENTED
│   └── memory.py                  # SQLite storage
│
├── config/                        # 🟡 CONFIGURATION 
│   └── langchain_config.yaml      # LangChain & RAG settings template
│
└── examples/                      # ✅ IMPLEMENTED
    ├── simple_demo.py             # No dependencies demo
    └── message_processing_demo.py # Full featured demo
```

## 🚀 Run the Demo (No Installation Required)

```bash
cd WorkEase
python3 examples/simple_demo.py
```

**Output:**
```
WorkEase Backend Demo - Message Processing Pipeline
====================================================================

📬 Processing 4 messages...

━━━ Message 1/4: GMAIL ━━━

📧 FROM: boss@company.com
📋 SUBJECT: Q4 Report Due Tomorrow
📝 CONTENT: Hi team, we need the quarterly report...

🤖 AI SUMMARY:
   boss@company.com requests urgent completion of report by end of day.

✅ EXTRACTED TASKS (2):
   1. Prepare and submit report 🔴 [Priority: 9/10]
      ⏰ Deadline: Today EOD
   2. Attend/prepare for meeting 🟡 [Priority: 6/10]

✓ Successfully processed 4 messages!
```

## 🔧 How It Works

### The Pipeline

```
Message → Orchestrator → LLM Summary → LLM Task Extraction → Result
```

### Code Example

```python
from core.orchestrator import Orchestrator, Message, MessageSource
from core.llm_client import MockLLMClient

# Initialize
llm = MockLLMClient()
orchestrator = Orchestrator(llm)

# Create message (normally comes from Gmail/Slack agent)
message = Message(
    id="msg_001",
    source=MessageSource.GMAIL,
    sender="boss@company.com",
    content="Please send the report by EOD today."
)

# Process through pipeline
result = await orchestrator.process_message(message)

# Result contains:
# - result['summary']: AI-generated summary
# - result['tasks']: Extracted tasks with priorities
```

## 🏗️ Architecture

```
┌─────────────────────────┐
│   Gmail/Slack Agents    │ (STUB - API integration pending)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     Orchestrator        │ ✅ Coordinates processing
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│      LLM Client         │ ✅ AI reasoning (Mock/Ollama)
│   • Summarize           │
│   • Extract tasks       │
│   • Analyze sentiment   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Database (SQLite)     │ ✅ Persist messages/tasks
└─────────────────────────┘
```

## 📝 Key Components

### 1. **Orchestrator** (`core/orchestrator.py`)
Central coordinator that:
- Receives messages from agents
- Calls LLM for summarization
- Calls LLM for task extraction
- Returns structured results

### 2. **LLM Client** (`core/llm_client.py`)
AI interface that provides:
- `MockLLMClient` - Simple keyword-based (no dependencies)
- `OllamaLLMClient` - Real AI via local Ollama (requires install)
- Swappable design (easy to add OpenAI, Anthropic, etc.)

### 3. **Database** (`database/memory.py`)
SQLite-based storage for:
- Messages (raw incoming)
- Summaries (AI-generated)
- Tasks (extracted actionables)
- Context (conversation history)

### 4. **Agents** (`agents/`)
Interface-ready for Gmail and Slack:
- `GmailAgent` - OAuth, fetch, send emails (STUB)
- `SlackAgent` - OAuth, channels, messages (STUB)

## 🔜 What's NOT Implemented Yet

- ❌ Gmail API integration (agent stub only)
- ❌ Slack API integration (agent stub only) 
- ❌ Event bus (direct communication for now)
- ❌ UI integration (backend only)
- ❌ Voice interface (STT/TTS)
- ❌ Real-time polling for new messages

## 🟡 LangChain & RAG Foundation (Ready for Future)

We've created the foundation for LangChain and RAG (Retrieval-Augmented Generation):

- ✅ **`context_provider.py`** - Protocol interface for all memory providers
- 🟡 **`langchain_memory.py`** - Enhanced conversation memory (structure ready)
- 🟡 **`rag_provider.py`** - Semantic search with vector DB (structure ready)
- 🟡 **`langchain_orchestrator.py`** - LLM with reasoning chains (structure ready)
- 🟡 **`langchain_config.yaml`** - Configuration template

These components provide a **future upgrade path** when you need:
- **Long-term memory** that remembers past conversations
- **Semantic search** across all messages
- **Chain-of-thought reasoning** for complex decisions
- **Multiple agent coordination** through LangChain agents

## 🎯 Next Implementation Steps

### Step 1: Gmail Agent (High Priority)
```python
# In agents/gmail_agent.py - implement these TODOs:
# - OAuth2 authentication flow
# - fetch_new_messages() using Gmail API
# - send_message() using Gmail API
# - mark_as_read() functionality
```

### Step 2: Slack Agent (High Priority)
```python
# In agents/slack_agent.py - implement these TODOs:
# - Slack OAuth authentication
# - fetch_messages() from channels/DMs
# - send_message() to channels
# - Real-time polling or webhooks
```

### Step 3: Connect to UI (Medium Priority)
```python
# In UI/ - integrate backend:
# - Display summaries in notification_dialog.py
# - Show extracted tasks
# - Update workease_app.py to use orchestrator
```

### Step 4: Add Real Ollama LLM (Optional)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b  # ~2GB model

# Then in code, replace MockLLMClient with:
llm = OllamaLLMClient(model="llama3.2:3b")
```

## 📚 Documentation

- **Backend README**: `BACKEND_README.md` - Full architecture details
- **Design Specs**: `dev/specs/autoreturn/design.md`
- **Requirements**: `dev/specs/autoreturn/requirements.md`
- **Tasks List**: `dev/specs/autoreturn/tasks.md`

## 💡 Development Tips

1. **Start with simple_demo.py** - Understand the pipeline
2. **Test components individually** - Each module has examples in BACKEND_README.md
3. **Use Mock LLM first** - Faster iteration, no external dependencies
4. **Read the specs** - Comprehensive design in `dev/specs/autoreturn/`
5. **Follow the architecture** - Keep modular, use interfaces

## 🧪 Testing

```bash
# Test orchestrator
python3 -c "
import asyncio
from core.orchestrator import Orchestrator, Message, MessageSource
from core.llm_client import MockLLMClient

async def test():
    llm = MockLLMClient()
    await llm.initialize()
    orch = Orchestrator(llm)
    
    msg = Message(
        id='test', 
        source=MessageSource.GMAIL,
        sender='test@example.com',
        content='Please submit the report by tomorrow.'
    )
    
    result = await orch.process_message(msg)
    print(f'Summary: {result[\"summary\"].summary}')
    print(f'Tasks: {len(result[\"tasks\"])}')

asyncio.run(test())
"
```

## 🤝 Team

**WorkEase FYP Team**
- Hasnain Saleem
- Alishba Tariq
- Kashan Saeed

**Supervisor**: Dr. Nouman Azam  
**Institution**: FAST-NUCES Peshawar

---

## 🔄 Activating LangChain/RAG (When Ready)

When you need more advanced features:

```python
# 1. Install dependencies
# Uncomment LangChain packages in requirements.txt
pip install -r requirements.txt

# 2. Use in your code
from core.memory.langchain_memory import LangChainMemoryProvider

# Initialize
memory = LangChainMemoryProvider(
    memory_type="buffer_summary",  # Remembers conversation history
    max_tokens=2000                # Context window size
)
await memory.initialize()

# The orchestrator stays the same - memory is swappable!
orchestrator = Orchestrator(llm, memory=memory)
```

## Summary

✅ **Backend Pipeline**: Fully functional  
✅ **LLM Integration**: Interface ready (Mock + Ollama)  
✅ **Database**: SQLite storage implemented  
🔶 **Agents**: Interfaces ready, APIs pending  
🟡 **LangChain/RAG**: Foundation ready for future activation  
❌ **UI Connection**: Not yet integrated  

**Status**: Core backend complete, ready for agent implementation and UI integration.