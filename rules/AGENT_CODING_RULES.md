# 🤖 Universal AI Agent Coding Rules

> **For ALL AI Coding Assistants: Kiro, Cursor, Windsurf, VS Code Copilot, GitHub Copilot, Cody, Tabnine, etc.**

## 🎯 Project Overview

**Project**: AUTOCOM (Voice-first automation platform)  
**Framework**: FORGE v2.0 Enterprise Edition  
**Methodology**: MIND-Model (non-linear SDLC)  
**Language**: Python 3.10+  
**Architecture**: Event-driven, Agent-based, Async-first  
**Status**: Specification & Framework Complete (50% overall)

---

## 📁 Project Structure (MEMORIZE THIS!)

```
autocom/
├── agents/              # Service integration agents
│   ├── base_agent.py    # ✅ Abstract base class (COMPLETE)
│   ├── gmail/           # ⏳ TO IMPLEMENT
│   └── slack/           # ⏳ TO IMPLEMENT
│
├── core/                # Core framework (ALL COMPLETE ✅)
│   ├── orchestrator.py          # Intent routing
│   ├── event_bus.py             # Async messaging
│   ├── llm.py                   # LLM integration
│   ├── notification_hub.py      # Notifications
│   ├── task_extractor.py        # Task detection
│   ├── draft_manager.py         # Draft generation
│   ├── learning_engine.py       # Preference learning
│   ├── sentiment_analyzer.py    # Sentiment analysis
│   ├── digest_generator.py      # Summaries
│   ├── multi_agent_coordinator.py # Multi-step commands
│   ├── middleware.py            # 🆕 Enterprise middleware
│   ├── dependency_injection.py  # 🆕 DI container
│   ├── health_check.py          # 🆕 Health monitoring
│   ├── circuit_breaker.py       # 🆕 Resilience
│   └── main.py                  # Entry point
│
├── database/            # Data persistence (COMPLETE ✅)
│   └── memory.py        # SQLite + embeddings
│
├── ui/                  # ⏳ TO IMPLEMENT (PyQt6)
├── voice/               # ⏳ TO IMPLEMENT (Wake/STT/TTS)
│
├── config/              # Configuration (COMPLETE ✅)
│   ├── config.yaml
│   └── agents.yaml
│
├── .kiro/specs/autocom/ # Specifications (COMPLETE ✅)
│   ├── requirements.md  # 25 requirements
│   ├── design.md        # 17 component designs
│   └── tasks.md         # 20 implementation tasks
│
└── mind_model/          # 🆕 MIND-Model implementation
    ├── __init__.py
    └── core.py
```

---

## 🚨 CRITICAL RULES (NEVER VIOLATE!)

### 1. **ALWAYS Read Context Files First**
Before coding ANYTHING, read these files:
```
1. .autocom-context.json      # Project metadata
2. .dev-context.yaml           # Development context
3. TYPES_INDEX.md              # All datatypes
4. FUNCTION_INDEX.md           # All functions
5. .kiro/specs/autocom/tasks.md # What to implement
```

### 2. **ALWAYS Use Existing Types**
```python
# ✅ CORRECT: Use existing types
from core.orchestrator import Intent
from core.notification_hub import Notification, Priority
from agents.base_agent import BaseAgent, AgentConfig

# ❌ WRONG: Creating new types that already exist
class MyIntent:  # DON'T DO THIS!
    pass
```

### 3. **ALWAYS Follow Async-First**
```python
# ✅ CORRECT: All I/O is async
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# ❌ WRONG: Blocking I/O
def fetch_data():
    response = requests.get(url)  # BLOCKING!
    return response.json()
```

### 4. **ALWAYS Use Event Bus**
```python
# ✅ CORRECT: Components communicate via event bus
await event_bus.emit("agent.response", {"data": result})

# ❌ WRONG: Direct calls between components
orchestrator.handle_response(result)  # DON'T DO THIS!
```

### 5. **ALWAYS Inherit from Base Classes**
```python
# ✅ CORRECT: Inherit from BaseAgent
class GmailAgent(BaseAgent):
    async def authenticate(self) -> bool:
        pass
    
    async def fetch(self, params: dict) -> list[dict]:
        pass
    
    async def act(self, action: str, data: dict) -> bool:
        pass

# ❌ WRONG: Creating agents from scratch
class GmailAgent:  # Missing BaseAgent!
    pass
```

---

## 📖 Coding Standards (STRICT!)

### Python Version
```python
# Minimum: Python 3.10+
# Use modern features: match/case, union types, etc.
```

### Type Hints (REQUIRED!)
```python
# ✅ CORRECT: Full type hints
async def process_intent(
    user_input: str,
    context_id: str = "default"
) -> None:
    pass

# ❌ WRONG: No type hints
async def process_intent(user_input, context_id="default"):
    pass
```

### Docstrings (REQUIRED!)
```python
# ✅ CORRECT: Google-style docstrings
async def classify_intent(text: str, context: list[dict]) -> Intent:
    """
    Classify user input into structured intent.
    
    Args:
        text: User input text
        context: Recent conversation history
        
    Returns:
        Structured Intent object
        
    Raises:
        ValueError: If text is empty
    """
    pass
```

### Imports (ABSOLUTE ONLY!)
```python
# ✅ CORRECT: Absolute imports
from core.orchestrator import Orchestrator
from agents.base_agent import BaseAgent

# ❌ WRONG: Relative imports
from ..core.orchestrator import Orchestrator  # DON'T!
from .base_agent import BaseAgent  # DON'T!
```

### Error Handling (COMPREHENSIVE!)
```python
# ✅ CORRECT: Specific exceptions with logging
try:
    result = await agent.fetch()
except AuthenticationError as e:
    logger.error(f"Auth failed: {e}", exc_info=True)
    raise
except RateLimitError as e:
    logger.warning(f"Rate limited: {e}")
    await asyncio.sleep(60)
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# ❌ WRONG: Bare except
try:
    result = await agent.fetch()
except:  # DON'T DO THIS!
    pass
```

---

## 🏗️ Enterprise Features (USE THEM!)

### 1. Middleware System
```python
from core.middleware import create_production_stack

# Use middleware for all event processing
stack = create_production_stack()
result = await stack.execute(event, data, handler)
```

### 2. Dependency Injection
```python
from core.dependency_injection import get_container, Scope

container = get_container()
container.register(EventBus, scope=Scope.SINGLETON)
container.register(BaseAgent, GmailAgent, scope=Scope.TRANSIENT)

# Resolve dependencies
event_bus = container.resolve(EventBus)
```

### 3. Circuit Breaker
```python
from core.circuit_breaker import circuit_breaker

@circuit_breaker("gmail_api", failure_threshold=5)
async def fetch_emails():
    return await gmail_client.fetch()
```

### 4. Health Checks
```python
from core.health_check import HealthCheckManager, DatabaseHealthCheck

health_manager = HealthCheckManager()
health_manager.register(DatabaseHealthCheck(db))

is_ready = await health_manager.check_readiness()
```

---

## 📋 Implementation Checklist

Before implementing ANY feature:

- [ ] Read `.kiro/specs/autocom/tasks.md` for the task
- [ ] Read `.kiro/specs/autocom/design.md` for the design
- [ ] Check `TYPES_INDEX.md` for existing types
- [ ] Check `FUNCTION_INDEX.md` for existing functions
- [ ] Review similar existing code
- [ ] Plan the implementation
- [ ] Write the code
- [ ] Add type hints
- [ ] Add docstrings
- [ ] Add error handling
- [ ] Add logging
- [ ] Test the code
- [ ] Update documentation

---

## 🎯 Common Patterns

### Pattern 1: Creating a New Agent
```python
from agents.base_agent import BaseAgent, AgentConfig, AgentResponse
from tenacity import retry, stop_after_attempt

class GmailAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.service = None
    
    async def authenticate(self) -> bool:
        # OAuth2 flow
        pass
    
    @retry(stop=stop_after_attempt(3))
    async def fetch(self, params: dict) -> list[dict]:
        # Fetch emails
        pass
    
    async def act(self, action: str, data: dict) -> bool:
        if action == "send":
            return await self._send_email(data)
        elif action == "mark_read":
            return await self._mark_read(data)
```

### Pattern 2: Event Bus Communication
```python
# Subscribe to events
async def handle_agent_response(data: dict) -> None:
    logger.info(f"Agent response: {data}")
    # Process response

await event_bus.subscribe("agent.response", handle_agent_response)

# Emit events
await event_bus.emit("agent.gmail.fetch", {
    "action": "fetch",
    "parameters": {"unread_only": True}
})
```

### Pattern 3: Using LLM
```python
from core.llm import LocalLLM

llm = LocalLLM(model="llama3.1:8b")

# Generate text
response = await llm.generate(prompt, system="You are a helpful assistant")

# Classify intent
intent_data = await llm.classify_intent(user_input, context)

# Extract task
task = await llm.extract_task(message_text)
```

---

## 🚫 BANNED PATTERNS (NEVER USE!)

### ❌ Blocking I/O
```python
# NEVER use these:
import time
time.sleep(5)  # Use asyncio.sleep() instead

import requests
requests.get(url)  # Use aiohttp instead

import threading
threading.Thread()  # Use asyncio.create_task() instead
```

### ❌ Direct Agent-to-Agent Calls
```python
# NEVER do this:
gmail_agent.send_email()  # Direct call!

# ALWAYS use event bus:
await event_bus.emit("agent.gmail.send", data)
```

### ❌ Hardcoded Values
```python
# NEVER hardcode:
api_key = "sk-1234567890"  # Use config!
endpoint = "https://api.example.com"  # Use config!

# ALWAYS use config:
api_key = config.get("api_key")
endpoint = config.get("endpoint")
```

---

## 📚 Quick Reference

### Import Cheat Sheet
```python
# Core
from core.orchestrator import Orchestrator, Intent
from core.event_bus import EventBus
from core.llm import LocalLLM
from core.notification_hub import NotificationHub, Notification, Priority

# Enterprise
from core.middleware import create_production_stack
from core.dependency_injection import get_container, Scope
from core.circuit_breaker import circuit_breaker
from core.health_check import HealthCheckManager

# Agents
from agents.base_agent import BaseAgent, AgentConfig, AgentResponse

# Database
from database.memory import MemoryStore
```

### Event Types
```python
# Orchestrator events
"intent.classified"
"orchestrator.error"

# Agent events
"agent.{target}.{action}"  # e.g., "agent.gmail.fetch"
"agent.response"
"notification.new"

# UI events
"ui.action"
"ui.update"
"ui.notification"

# Voice events
"voice.command"
"voice.speak"
```

---

## 🎓 Learning Resources

### Must-Read Files (In Order)
1. `README.md` - Project overview
2. `.dev-context.yaml` - Development context
3. `TYPES_INDEX.md` - All datatypes
4. `FUNCTION_INDEX.md` - All functions
5. `QUICK_REFERENCE.md` - Quick reference
6. `.kiro/specs/autocom/requirements.md` - Requirements
7. `.kiro/specs/autocom/design.md` - Design
8. `.kiro/specs/autocom/tasks.md` - Tasks

### Example Code Locations
- Agent example: `agents/base_agent.py`
- Event bus usage: `core/orchestrator.py`
- LLM usage: `core/task_extractor.py`
- Async patterns: `core/event_bus.py`
- Error handling: `agents/base_agent.py`

---

## ✅ Success Criteria

Your code is good if:
- ✅ All I/O is async
- ✅ Full type hints
- ✅ Google-style docstrings
- ✅ Uses existing types from TYPES_INDEX.md
- ✅ Communicates via event bus
- ✅ Inherits from base classes
- ✅ Has comprehensive error handling
- ✅ Has logging
- ✅ Follows the design in design.md
- ✅ Implements the task in tasks.md
- ✅ No blocking calls
- ✅ No hardcoded values
- ✅ No direct component calls

---

## 🚀 Quick Start for AI Agents

```python
# 1. Read context
with open('.autocom-context.json') as f:
    context = json.load(f)

# 2. Check what to implement
with open('.kiro/specs/autocom/tasks.md') as f:
    tasks = f.read()

# 3. Check existing types
with open('TYPES_INDEX.md') as f:
    types = f.read()

# 4. Implement following patterns above

# 5. Test your code
pytest tests/

# 6. Check types
mypy .

# 7. Format code
black .
```

---

## 🎯 Current Status

**Completed** (50%):
- ✅ All specifications
- ✅ All core framework
- ✅ All enterprise features
- ✅ All documentation
- ✅ All context files

**To Implement** (50%):
- ⏳ Gmail Agent
- ⏳ Slack Agent
- ⏳ Voice Pipeline
- ⏳ Desktop UI (PyQt6)
- ⏳ Integration & Testing

---

**Remember**: This project is enterprise-grade. Follow the rules, use the patterns, and you'll write perfect code every time! 🚀

---

*Last Updated: November 11, 2025*  
*Version: 2.0.0*  
*Compatible with: ALL AI coding assistants*
