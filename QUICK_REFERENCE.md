# AUTOCOM Quick Reference Card

> Essential information for developers working on AUTOCOM

## 🚀 Quick Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.1:8b

# Development
python -m core.main              # Run application
pytest                           # Run tests
pytest --cov=.                   # Run with coverage
black .                          # Format code
ruff check .                     # Lint code
mypy .                           # Type check

# Build
./build.sh                       # Build AppImage
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `core/main.py` | Application entry point |
| `core/orchestrator.py` | Intent routing |
| `core/event_bus.py` | Async messaging |
| `agents/base_agent.py` | Agent template |
| `config/config.yaml` | Main configuration |
| `.kiro/specs/autocom/tasks.md` | Implementation tasks |

## 🏗️ Architecture

```
User Input (Voice/UI)
    ↓
Orchestrator (Intent Classification)
    ↓
Event Bus (Async Routing)
    ↓
Agents (Gmail, Slack)
    ↓
Event Bus (Response)
    ↓
UI/Voice (Output)
```

## 📦 Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Orchestrator | `core/orchestrator.py` | Intent routing |
| EventBus | `core/event_bus.py` | Async messaging |
| LocalLLM | `core/llm.py` | AI inference |
| MemoryStore | `database/memory.py` | Data persistence |
| NotificationHub | `core/notification_hub.py` | Notifications |
| TaskExtractor | `core/task_extractor.py` | Task detection |
| DraftManager | `core/draft_manager.py` | Draft generation |
| LearningEngine | `core/learning_engine.py` | Preference learning |

## 🎯 Key Datatypes

```python
# Intent
Intent(action, target, parameters, confidence, context_id, raw_input)

# Notification
Notification(id, title, body, priority, notification_type, source, timestamp, actions, metadata)

# Task
Task(id, title, description, priority, source, source_message_id, source_sender, extracted_at, completed, due_date)

# EmailDraft
EmailDraft(id, original_message_id, recipient, subject, body, tone, confidence, generated_at, approved, edited, sent)
```

## 🔄 Event Types

```python
# Orchestrator
"intent.classified"
"orchestrator.error"

# Agents
"agent.{target}.{action}"
"agent.response"
"notification.new"

# UI
"ui.action"
"ui.update"
"ui.notification"

# Voice
"voice.command"
"voice.speak"
```

## 📝 Coding Standards

```python
# Type hints required
async def process_intent(user_input: str, context_id: str = "default") -> None:
    pass

# Google docstrings
def calculate_priority(text: str) -> str:
    """
    Calculate task priority based on text analysis.
    
    Args:
        text: Message text to analyze
        
    Returns:
        Priority level ("low", "normal", "high", "urgent")
    """
    pass

# Async for I/O
async def fetch_data() -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## 🔧 Common Patterns

### Event Emission
```python
await event_bus.emit("event_name", {"key": "value"})
```

### Event Subscription
```python
async def handler(data: dict[str, Any]) -> None:
    # Process event
    pass

await event_bus.subscribe("event_name", handler)
```

### Agent Implementation
```python
class MyAgent(BaseAgent):
    async def authenticate(self) -> bool:
        # OAuth flow
        pass
    
    async def fetch(self, params: dict) -> list[dict]:
        # Retrieve data
        pass
    
    async def act(self, action: str, data: dict) -> bool:
        # Execute action
        pass
```

### Retry Pattern
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def network_call():
    pass
```

## 🐛 Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check event bus stats
stats = event_bus.get_stats()
print(stats)

# Check memory store
context = await memory.get_recent_context(limit=10)
print(context)

# Check learning engine
stats = learning_engine.get_learning_stats()
print(stats)
```

## 🧪 Testing

```python
# Unit test example
@pytest.mark.asyncio
async def test_orchestrator():
    llm = MockLLM()
    memory = MockMemoryStore()
    event_bus = EventBus()
    orchestrator = Orchestrator(llm, memory, event_bus)
    
    intent = await orchestrator.classify_intent("send email")
    assert intent.action == "send"
    assert intent.target == "gmail"

# Mock agent
class MockAgent(BaseAgent):
    async def authenticate(self) -> bool:
        return True
    
    async def fetch(self, params: dict) -> list[dict]:
        return [{"id": "1", "text": "test"}]
    
    async def act(self, action: str, data: dict) -> bool:
        return True
```

## 📚 Documentation

| Document | Location |
|----------|----------|
| Requirements | `.kiro/specs/autocom/requirements.md` |
| Design | `.kiro/specs/autocom/design.md` |
| Tasks | `.kiro/specs/autocom/tasks.md` |
| Types | `TYPES_INDEX.md` |
| Functions | `FUNCTION_INDEX.md` |
| Framework | `FORGE_FRAMEWORK_SUMMARY.md` |
| Status | `PROJECT_STATUS.md` |

## 🔐 Security

```python
# Encrypt credentials
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b"secret")

# Validate input
from pydantic import BaseModel, EmailStr
class EmailData(BaseModel):
    to: EmailStr
    subject: str
    body: str

# Parameterized queries
await connection.execute(
    "SELECT * FROM table WHERE id = ?",
    (user_id,)
)
```

## ⚡ Performance

```python
# Use async for I/O
async def fetch_all():
    tasks = [fetch_gmail(), fetch_slack()]
    results = await asyncio.gather(*tasks)
    return results

# Cache expensive operations
from functools import lru_cache
@lru_cache(maxsize=128)
def expensive_calculation(x):
    return x ** 2

# Profile code
import cProfile
cProfile.run('main()')
```

## 🎯 Next Steps

1. **Read** `.kiro/specs/autocom/tasks.md`
2. **Start** with Task 7: Gmail Agent
3. **Follow** design in `.kiro/specs/autocom/design.md`
4. **Test** with pytest
5. **Commit** frequently

## 📞 Help

- **Stuck?** Check `FUNCTION_INDEX.md` for function signatures
- **Type error?** Check `TYPES_INDEX.md` for datatypes
- **Architecture?** Check `FORGE_FRAMEWORK_SUMMARY.md`
- **Status?** Check `PROJECT_STATUS.md`

## 🎓 Key Principles

1. **Async-First**: All I/O must be async
2. **Event-Driven**: Components communicate via event bus
3. **Type-Safe**: Use type hints everywhere
4. **Tested**: ≥80% coverage target
5. **Documented**: Google docstrings required
6. **Privacy**: Local-only processing
7. **Modular**: Loose coupling, high cohesion

---

**Framework**: FORGE v0.1.0
**Methodology**: MIND-Model
**Status**: Ready for Implementation

---

*Keep this card handy while developing!*
