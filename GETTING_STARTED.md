# Getting Started with AUTOCOM Development

## 🎯 Quick Start Checklist

This guide helps you get from "project downloaded" to "ready to implement" in under 30 minutes.

---

## ✅ Phase 1: Environment Setup (10 minutes)

### 1. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### 2. Choose and Install LLM Model

**For Weak PC (4-6GB RAM)** - Recommended:
```bash
ollama pull llama3.2:3b
```

**For Standard PC (8GB+ RAM)**:
```bash
ollama pull llama3.1:8b
```

**For Very Weak PC (2-4GB RAM)**:
```bash
ollama pull tinyllama
```

See [Model Selection Guide](docs/MODEL_SELECTION.md) for details.

### 3. Test Ollama

```bash
# Test the model works
ollama run llama3.2:3b "Hello, how are you?"

# Should respond with a greeting
# Press Ctrl+D to exit
```

### 4. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ✅ Phase 2: Understand the Project (15 minutes)

### 1. Read Architecture Summary

**File**: `.kiro/specs/autocom/ARCHITECTURE_SUMMARY.md`

**Key Points**:
- Current status: Framework complete, agents need implementation
- Architecture is future-proof (LangChain/RAG ready)
- Weak PC support with multiple model options

### 2. Review Requirements

**File**: `.kiro/specs/autocom/requirements.md`

**What to Look For**:
- 25 requirements covering all use cases
- User stories and acceptance criteria
- What the system should do

### 3. Check Design Document

**File**: `.kiro/specs/autocom/design.md`

**What to Look For**:
- Component architecture
- How pieces fit together
- Interface definitions

### 4. Review Implementation Plan

**File**: `.kiro/specs/autocom/tasks.md`

**What to Look For**:
- 20 major tasks with sub-tasks
- What's already done (Tasks 1-6 mostly complete)
- What needs implementation (Tasks 7-20)

---

## ✅ Phase 3: API Research (30-60 minutes)

### 1. Gmail API Research

**Official Docs**: https://developers.google.com/gmail/api

**What to Learn**:
- OAuth2 authentication flow
- How to fetch emails (`users.messages.list`)
- How to send emails (`users.messages.send`)
- Required scopes
- Rate limits

**Key Endpoints**:
```
GET /gmail/v1/users/me/messages
POST /gmail/v1/users/me/messages/send
POST /gmail/v1/users/me/messages/{id}/modify
```

**Take Notes On**:
- Authentication steps
- API request/response format
- Error handling
- Rate limits

### 2. Slack API Research

**Official Docs**: https://api.slack.com/

**What to Learn**:
- OAuth2 with workspace scope
- How to fetch messages (`conversations.history`)
- How to post messages (`chat.postMessage`)
- WebSocket/Socket Mode for real-time events
- Rate limiting

**Key Endpoints**:
```
GET /conversations.history
POST /chat.postMessage
POST /reactions.add
```

**Take Notes On**:
- Authentication flow
- WebSocket connection setup
- Message format
- Rate limits

### 3. Create Test Accounts

**Gmail**:
1. Go to Google Cloud Console
2. Create new project
3. Enable Gmail API
4. Create OAuth2 credentials
5. Download credentials.json

**Slack**:
1. Go to api.slack.com/apps
2. Create new app
3. Add OAuth scopes
4. Install to workspace
5. Get OAuth token

---

## ✅ Phase 4: Test Current Code (15 minutes)

### 1. Test LLM Integration

Create `test_llm.py`:

```python
import asyncio
from core.llm import LocalLLM

async def test():
    llm = LocalLLM(model="llama3.2:3b")
    
    # Test basic generation
    response = await llm.generate("Hello, how are you?")
    print(f"Response: {response}")
    
    # Test intent classification
    intent = await llm.classify_intent(
        "Send an email to john@example.com",
        context=[]
    )
    print(f"Intent: {intent}")
    
    await llm.close()

asyncio.run(test())
```

Run:
```bash
python test_llm.py
```

**Expected**: Should see LLM responses and intent classification.

### 2. Test Event Bus

Create `test_event_bus.py`:

```python
import asyncio
from core.event_bus import EventBus

async def test():
    bus = EventBus()
    
    # Subscribe to event
    received = []
    async def handler(data):
        received.append(data)
        print(f"Received: {data}")
    
    await bus.subscribe("test.event", handler)
    
    # Emit event
    await bus.emit("test.event", {"message": "Hello!"})
    
    # Wait a bit
    await asyncio.sleep(0.1)
    
    assert len(received) == 1
    print("✅ Event bus works!")

asyncio.run(test())
```

Run:
```bash
python test_event_bus.py
```

### 3. Test Memory Store

Create `test_memory.py`:

```python
import asyncio
from database.memory import MemoryStore
from core.orchestrator import Intent

async def test():
    memory = MemoryStore(db_path="test_memory.db")
    await memory.initialize()
    
    # Store interaction
    intent = Intent(
        action="fetch",
        target="gmail",
        parameters={},
        confidence=0.9,
        context_id="test",
        raw_input="Check my emails"
    )
    
    await memory.store_interaction(intent, "Found 5 emails")
    
    # Retrieve context
    context = await memory.get_recent_context(limit=10)
    print(f"Context: {context}")
    
    assert len(context) > 0
    print("✅ Memory store works!")
    
    await memory.close()

asyncio.run(test())
```

Run:
```bash
python test_memory.py
```

---

## ✅ Phase 5: Ready to Implement!

### Current Status

**✅ Complete**:
- Core framework (orchestrator, event bus, LLM)
- Memory store with SQLite
- Base agent abstraction
- Configuration system
- Documentation

**⏳ Needs Implementation**:
- Gmail Agent (Task 7)
- Slack Agent (Task 8)
- Jira Agent (Task 9)
- Voice Pipeline (Task 10)
- Desktop UI (Task 12)
- Wiring everything together (Task 15)

### Next Steps

**Option 1: Start with Gmail Agent** (Recommended)
- Follow Task 7 in `tasks.md`
- Implement OAuth2 authentication
- Implement email fetching
- Implement email sending
- Write tests

**Option 2: Start with Slack Agent**
- Follow Task 8 in `tasks.md`
- Implement OAuth2 authentication
- Implement message fetching
- Implement WebSocket listener
- Write tests

**Option 3: Build UI First**
- Follow Task 12 in `tasks.md`
- Create PyQt6 dashboard
- Build unified inbox table
- Add system tray
- Test with mock data

### Recommended Order

1. **Gmail Agent** (Task 7) - 1-2 days
2. **Slack Agent** (Task 8) - 1-2 days
3. **Basic UI** (Task 12) - 2-3 days
4. **Wire Together** (Task 15) - 1 day
5. **Voice Pipeline** (Task 10) - 2-3 days
6. **Polish & Test** (Tasks 17-20) - 1-2 weeks

---

## 📚 Key Documents Reference

### Must Read (30 minutes):
1. [Architecture Summary](.kiro/specs/autocom/ARCHITECTURE_SUMMARY.md)
2. [Model Selection Guide](docs/MODEL_SELECTION.md)
3. [Requirements](.kiro/specs/autocom/requirements.md) - Skim through

### Reference When Needed:
4. [Design Document](.kiro/specs/autocom/design.md) - Component details
5. [Implementation Plan](.kiro/specs/autocom/tasks.md) - Task breakdown
6. [LangChain/RAG Upgrade](.kiro/specs/autocom/LANGCHAIN_RAG_UPGRADE.md) - Future

---

## 🎯 Success Criteria

You're ready to start implementing when:

- ✅ Ollama installed and model pulled
- ✅ Python environment set up
- ✅ Dependencies installed
- ✅ LLM test passes
- ✅ Event bus test passes
- ✅ Memory store test passes
- ✅ Gmail API research complete
- ✅ Slack API research complete
- ✅ You understand the architecture

---

## 🆘 Troubleshooting

### Ollama Not Working

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama service
sudo systemctl start ollama

# Check logs
journalctl -u ollama -f
```

### Python Dependencies Fail

```bash
# Update pip
pip install --upgrade pip

# Install one by one to find issue
pip install pydantic
pip install pyyaml
# etc...
```

### Model Download Slow

```bash
# Check download progress
ollama list

# If stuck, cancel and retry
# Ctrl+C
ollama pull llama3.2:3b
```

### Out of Memory

**Solution**: Use smaller model
```bash
ollama pull tinyllama  # Only 637MB
```

Update config:
```yaml
orchestrator:
  llm_model: "tinyllama"
```

---

## 💡 Tips

1. **Start Small**: Implement one agent at a time
2. **Test Often**: Write tests as you go
3. **Use Mock Data**: Test UI without real APIs first
4. **Read Docs**: Gmail/Slack API docs are your friends
5. **Ask Questions**: Check existing code for patterns
6. **Commit Often**: Git commit after each working feature

---

## 🚀 You're Ready!

**Current Status**: ✅ Environment set up, ready to code

**Next Action**: Choose a task from `tasks.md` and start implementing!

**Recommended**: Start with **Task 7 (Gmail Agent)**

**Good Luck!** 🎉

---

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Run tests
python test_llm.py
python test_event_bus.py
python test_memory.py

# Check Ollama models
ollama list

# Test Ollama
ollama run llama3.2:3b "test"

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Run AUTOCOM (when ready)
python -m core.main
```
