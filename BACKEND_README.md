# AutoReturn Backend Architecture

## 📋 Overview



## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AGENTS LAYER                         │
│  ┌─────────────┐  ┌─────────────┐                      │
│  │Gmail Agent  │  │Slack Agent  │  (STUB - Not impl.)  │
│  │(Future)     │  │(Future)     │                      │
│  └──────┬──────┘  └──────┬──────┘                      │
└─────────┼────────────────┼─────────────────────────────┘
          │                │
          └────────┬───────┘
                   ▼
         ┌─────────────────┐
         │   Message Queue  │
         └────────┬─────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│                ORCHESTRATOR LAYER                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Orchestrator                        │   │
│  │  • Receives messages from agents                 │   │
│  │  • Coordinates LLM analysis                      │   │
│  │  • Manages task extraction                       │   │
│  │  • Stores results in database                    │   │
│  └────────────┬─────────────────────────────────────┘   │
└───────────────┼──────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│                    LLM LAYER (BRAIN)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │        LLM Client (Local Ollama or Cloud)        │   │
│  │  • Message summarization                         │   │
│  │  • Task extraction and reasoning                 │   │
│  │  • Intent classification (future)                │   │
│  │  • Draft generation (future)                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│              ALGORITHMS & UTILITIES LAYER                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Task      │  │ Priority   │  │ Sentiment  │        │
│  │ Extractor  │  │ Scorer     │  │ Analyzer   │        │
│  │(Partial)   │  │ (Future)   │  │ (Future)   │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Memory Store (SQLite)                    │   │
│  │  • Messages storage                              │   │
│  │  • Summaries storage                             │   │
│  │  • Tasks storage                                 │   │
│  │  • Context/history storage                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
WorkEase/
├── core/                          # Core orchestration and LLM
│   ├── __init__.py
│   ├── models.py                  # ✅ Data models (Message, Task, etc.)
│   ├── llm_client.py              # ✅ LLM interface (Ollama/Mock)
│   ├── orchestrator.py            # ✅ Central coordinator
│   ├── langchain_orchestrator.py  # 🟡 Base for LangChain orchestration
│   └── memory/                    # Memory and context providers
│       ├── __init__.py
│       ├── context_provider.py    # ✅ Protocol interface
│       ├── langchain_memory.py    # 🟡 LangChain memory provider
│       └── rag_provider.py        # 🟡 RAG vector store provider
│
├── agents/                        # Communication service agents
│   ├── __init__.py
│   ├── base_agent.py              # ✅ Agent protocol/interface
│   ├── gmail_agent.py             # 🔶 STUB - API integration pending
│   └── slack_agent.py             # 🔶 STUB - API integration pending
│
├── algorithms/                    # Custom algorithms
│   ├── __init__.py
│   └── task_extractor.py          # ✅ Pattern-based task extraction
│
├── database/                      # Data persistence
│   ├── __init__.py
│   └── memory.py                  # ✅ SQLite memory store
│
├── examples/                      # Demo scripts
│   └── message_processing_demo.py # ✅ Full pipeline demo
│
├── UI/                           # PyQt6 UI (separate, existing)
│   └── ...                       # (Not modified in this task)
│
├── config/                       # Configuration files
│   └── langchain_config.yaml     # 🟡 LangChain & RAG settings
└── requirements.txt              # ✅ Python dependencies (with LangChain/RAG)
```

## ✅ What's Implemented

### 1. **Core Orchestrator** (`core/orchestrator.py`)
- ✅ Receives messages from agents
- ✅ Coordinates LLM for summarization
- ✅ Coordinates LLM for task extraction
- ✅ Returns structured results
- ✅ Batch processing support
- ✅ Error handling

### 2. **LLM Client** (`core/llm_client.py`)
- ✅ Abstract LLM interface (swappable implementations)
- ✅ Ollama client (local LLM support)
- ✅ Mock client (for testing without Ollama)
- ✅ Message analysis (sentiment, urgency, priority)
- ✅ Summary generation
- ✅ Task extraction
- ✅ Intent understanding (basic)
- ✅ Draft generation (basic)

### 3. **Data Models** (`core/models.py`)
- ✅ `Message` - Universal message format
- ✅ `MessageAnalysis` - LLM analysis results
- ✅ `Task` - Extracted actionable tasks
- ✅ `Intent` - User intent classification
- ✅ `Context` - Conversation history
- ✅ `Notification` - User notifications
- ✅ Enums for message sources, sentiment, tone, status

### 4. **Memory/Context Management** 
- ✅ `core/memory/context_provider.py` - Protocol interface for all memory providers
- ✅ `database/memory.py` - Simple SQLite storage (default)
- 🟡 `core/memory/langchain_memory.py` - Enhanced context with LangChain (base ready)
- 🟡 `core/memory/rag_provider.py` - Semantic search with RAG (base ready)
- ✅ Context tables for conversation history
- ✅ Full CRUD operations
- ✅ Query methods (recent messages, pending tasks, etc.)

### 5. **Task Extraction Algorithm** (`algorithms/task_extractor.py`)
- ✅ Pattern-based task detection
- ✅ Action verb recognition
- ✅ Modal verb analysis (must, should, need to)
- ✅ Urgency keyword detection
- ✅ Deadline extraction (multiple formats)
- ✅ Priority calculation
- ✅ Works with LLM analysis or standalone

### 6. **Demo System** (`examples/message_processing_demo.py`)
- ✅ Interactive demo menu
- ✅ Mock LLM demo (no dependencies)
- ✅ Real Ollama LLM demo
- ✅ Database persistence demo
- ✅ Pretty colored terminal output

## 🔶 What's Stubbed or Partially Implemented

### 1. **Gmail Agent** (`agents/gmail_agent.py`)
- 🔶 Gmail API authentication
- 🔶 Fetch messages from Gmail
- 🔶 Send emails via Gmail
- 🔶 Mark as read functionality
- 🔶 Polling for new messages

**Status**: Interface defined, methods stubbed with TODOs

### 2. **Slack Agent** (`agents/slack_agent.py`)
- 🔶 Slack OAuth authentication
- 🔶 Fetch messages from channels/DMs
- 🔶 Send messages to Slack
- 🔶 Channel management
- 🔶 Real-time message polling

**Status**: Interface defined, methods stubbed with TODOs

### 3. **Event Bus**
- 🔶 Pub/sub event system for component communication
- 🔶 Async event processing

**Status**: Not yet started

### 4. **Additional Algorithms**
- 🔶 Priority scorer (sentiment + urgency + sender weight)
- 🔶 Sentiment analyzer (more sophisticated than LLM basic)
- 🔶 Intent classifier (enhance current implementation)
- 🔶 Context matcher

**Status**: Not yet started

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **Optional: Ollama** (for real LLM, not required for mock demo)

### Installation

```bash
# 1. Navigate to WorkEase directory
cd WorkEase

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Optional: Install Ollama (for real LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (for weak PCs, use smaller model)
ollama pull llama3.2:3b  # ~2GB, works on weak PCs

# OR for better quality (needs 8GB+ RAM)
ollama pull llama3.1:8b  # ~4.7GB

# Start Ollama (usually auto-starts)
ollama serve
```

## 🎮 Running the Demos

### Demo 1: Mock LLM (No Ollama Required)

Fast, simple demo using keyword-based mock LLM.

```bash
cd WorkEase
python examples/message_processing_demo.py

# Choose option 1 at the menu
```

**What it demonstrates:**
- Message reception (mocked)
- Orchestrator processing
- Summary generation
- Task extraction
- Priority calculation

### Demo 2: Real Ollama LLM

Uses actual AI for reasoning and analysis.

```bash
# Make sure Ollama is running
ollama serve  # In separate terminal

# Run demo
python examples/message_processing_demo.py

# Choose option 2 at the menu
```

**What it demonstrates:**
- Real AI-powered summarization
- Intelligent task extraction
- Context-aware analysis
- Sentiment and urgency detection

### Demo 3: With Database Persistence

Shows full pipeline including storage.

```bash
python examples/message_processing_demo.py

# Choose option 3 at the menu
```

**What it demonstrates:**
- Message storage in SQLite
- Summary persistence
- Task storage with priorities
- Retrieval of stored data
- Pending tasks query

## 📊 Example Output

```
============================================================
WorkEase Message Processing Pipeline Demo
============================================================

🔧 Initializing Mock LLM (no Ollama needed)...
✓ Mock LLM ready

🎯 Initializing Orchestrator...
✓ Orchestrator ready

📬 Processing 4 messages...

──────────────────────────────────────────────────────────
Message 1/4: GMAIL
──────────────────────────────────────────────────────────

  📧 From: boss@company.com
  📋 Subject: Q4 Report Due Tomorrow
  📝 Content:
     Hi team, we need the quarterly report completed...

  🤖 AI SUMMARY:
     Team needs to prepare and send quarterly report by EOD.

  📌 KEY POINTS:
     • Complete Q4 report
     • Include metrics and analysis
     • Due by end of day

  📊 ANALYSIS:
     Sentiment: neutral
     Urgency: 9/10

  ✅ EXTRACTED TASKS (2):
     1. Prepare the quarterly report [Priority: 9/10]
        ⏰ Deadline: 2024-01-15T17:00:00
     2. Send report to boss [Priority: 9/10]

...
```

## 🔄 How the Pipeline Works

### Step-by-Step Flow

1. **Message Arrival** (Future: from Gmail/Slack agents)
   ```python
   message = Message(
       id="msg_001",
       source=MessageSource.GMAIL,
       sender="boss@company.com",
       content="Please complete the report by tomorrow..."
   )
   ```

2. **Orchestrator Processing**
   ```python
   result = await orchestrator.process_message(message)
   ```

3. **LLM Summarization**
   - Orchestrator calls `llm.generate_summary()`
   - LLM analyzes content, sender, context
   - Returns concise summary with key points

4. **Task Extraction**
   - Orchestrator calls `llm.extract_tasks()`
   - LLM identifies actionable items
   - Extracts deadlines, priorities, descriptions

5. **Result Structure**
   ```python
   {
       "message_id": "msg_001",
       "source": "gmail",
       "sender": "boss@company.com",
       "summary": MessageSummary(...),
       "tasks": [Task(...), Task(...)],
       "processed_at": "2024-01-15T10:30:00"
   }
   ```

6. **Storage** (Optional)
   ```python
   await memory.store_message(...)
   await memory.store_summary(...)
   await memory.store_tasks(...)
   ```

## 🧪 Testing Individual Components

### Test LLM Client

```python
import asyncio
from core.llm_client import MockLLMClient

async def test():
    llm = MockLLMClient()
    await llm.initialize()
    
    summary = await llm.generate_summary(
        message_content="Please send the report by EOD",
        source="gmail",
        sender="boss@company.com"
    )
    print(f"Summary: {summary}")
    
    tasks = await llm.extract_tasks("Please send the report and review the docs")
    print(f"Tasks: {tasks}")

asyncio.run(test())
```

### Test Database

```python
import asyncio
from database.memory import MemoryStore

async def test():
    memory = MemoryStore("test.db")
    await memory.initialize()
    
    await memory.store_message(
        message_id="test_001",
        source="gmail",
        sender="test@example.com",
        content="Test message"
    )
    
    messages = await memory.get_recent_messages(limit=5)
    print(f"Recent messages: {messages}")
    
    await memory.close()

asyncio.run(test())
```

## 🔜 Next Steps

### High Priority (Core Functionality)

1. **Implement Gmail Agent**
   - OAuth2 authentication flow
   - Gmail API integration
   - Message fetching and parsing
   - Send email functionality

2. **Implement Slack Agent**
   - Slack OAuth authentication
   - WebSocket/polling for real-time messages
   - Send message to channels/DMs
   - Channel management

3. **Implement Event Bus**
   - Async pub/sub system
   - Event types (message.received, task.created, etc.)
   - Subscribe/unsubscribe mechanism
   - Error isolation

4. **Connect to UI**
   - Display summaries in PyQt6 UI
   - Show extracted tasks
   - Notification system
   - Task management interface

### Medium Priority (Enhancement)

5. **Implement Priority Scorer Algorithm**
   - Sender weight calculation
   - Urgency score enhancement
   - Time decay for old messages

6. **Implement Sentiment Analyzer**
   - More sophisticated than LLM basic analysis
   - Train on custom dataset if needed

7. **Add Voice Pipeline**
   - Wake word detection
   - Speech-to-text (STT)
   - Text-to-speech (TTS)
   - Voice command processing

### Low Priority (Advanced Features)

8. **Upgrade to LangChain/RAG**
   - Follow guide in `dev/specs/autoreturn/LANGCHAIN_RAG_UPGRADE.md`
   - Enhanced context management
   - Semantic search across history

9. **Add Learning Engine**
   - User preference learning
   - Adaptive priority adjustment
   - Draft quality improvement

## 🐛 Known Issues / Limitations

1. **Gmail/Slack agents are stubs** - Need API implementation
2. **Event bus not implemented** - Components communicate directly
3. **No real-time polling** - Agents would need background tasks
4. **Mock LLM is simplistic** - Keyword-based, not real AI
5. **No authentication system** - Security needs implementation
6. **No rate limiting** - API calls could exceed quotas
7. **No caching** - LLM responses not cached

## 📚 Documentation References

- **Design Document**: `dev/specs/autoreturn/design.md`
- **Requirements**: `dev/specs/autoreturn/requirements.md`
- **Tasks**: `dev/specs/autoreturn/tasks.md`
- **Architecture Summary**: `dev/specs/autoreturn/ARCHITECTURE_SUMMARY.md`
- **LangChain Upgrade Guide**: `dev/specs/autoreturn/LANGCHAIN_RAG_UPGRADE.md`

## 💡 Tips for Development

1. **Start with Mock LLM** - Faster iteration, no Ollama dependency
2. **Use Database Demo** - Test persistence without full integration
3. **Check logs** - Orchestrator prints debug info
4. **Test incrementally** - Each component has test methods
5. **Read the specs** - Detailed design in `dev/specs/autoreturn/`
6. **LangChain/RAG ready** - Base implementation ready to activate when needed

## 📈 **LangChain & RAG Upgrade Path**

When you're ready to enhance the system with better memory and reasoning:

1. **Install dependencies**:
   ```bash
   # Uncomment LangChain dependencies in requirements.txt
   pip install -r requirements.txt
   ```

2. **Configure**:
   Edit `config/langchain_config.yaml` with your preferences:
   ```yaml
   memory:
     provider: "langchain"  # Change from "simple" to "langchain" or "rag"
     langchain:
       memory_type: "buffer_summary"
       max_tokens: 2000
   ```

3. **Activate the implementation**:
   - Uncomment the imports in the LangChain files
   - Complete any `TODO` sections marked in the code
   - Use the Context Provider protocol for easy swapping

4. **Code example**:
   ```python
   # Switch from simple to advanced memory
   # memory = MemoryStore(db_path="database/workease.db")
   memory = LangChainMemoryProvider(
       memory_type="buffer_summary",
       max_tokens=2000
   )
   
   # The orchestrator doesn't change - swappable by design!
   orchestrator = Orchestrator(llm, memory)
   ```

## 🤝 Contributing

When implementing new features:

1. Follow existing code structure
2. Add comprehensive docstrings
3. Include type hints
4. Create demo/test for the feature
5. Update this README
6. Check design doc for requirements

## 📝 License

Part of WorkEase Final Year Project - FAST-NUCES Peshawar

---

**Team**: Hasnain Saleem, Alishba Tariq, Kashan Saeed  
**Supervisor**: Dr. Nouman Azam

---

*Last Updated: January 2024*