# 🤖 AI Agent Onboarding Guide

> **Welcome to AUTOCOM! This guide will get you productive in 30 minutes.**

---

## 🎯 What You'll Learn

1. What AUTOCOM is and how it works
2. The FORGE Framework architecture
3. Critical coding rules you must follow
4. Where to find types, functions, and tasks
5. How to start coding immediately

---

## 📚 30-Minute Onboarding Path

### Phase 1: Understanding (10 minutes)

#### Step 1: Read the Entry Point (5 minutes)
📄 **File**: `rules/00-START-HERE.md`

**What you'll learn**:
- Project overview and status
- High-level architecture
- Critical rules summary
- Quick navigation guide

**Action**: Open and read this file now.

#### Step 2: Understand the Architecture (5 minutes)
📄 **File**: `README.md`

**What you'll learn**:
- AUTOCOM features and capabilities
- Technology stack
- Project goals

**Action**: Skim this file for context.

---

### Phase 2: Coding Rules (15 minutes)

#### Step 3: Learn the Coding Rules (15 minutes)
📄 **File**: `rules/AGENT_CODING_RULES.md`

**What you'll learn**:
- Project structure (memorize this!)
- 5 critical rules (NEVER violate!)
- Coding standards (Python 3.10+, async-first, type hints)
- Enterprise features (middleware, DI, circuit breaker, health checks)
- Common patterns (agents, event bus, LLM)
- Banned patterns (blocking I/O, direct calls, hardcoded values)
- Quick reference (imports, event types)

**Action**: Read this file carefully. It's your coding bible.

---

### Phase 3: Context & Resources (5 minutes)

#### Step 4: Load Context Files (3 minutes)
📄 **Files**:
- `.autocom-context.json` - Project metadata
- `.dev-context.yaml` - Development context
- `TYPES_INDEX.md` - All datatypes (use these!)
- `FUNCTION_INDEX.md` - All functions (reference these!)

**Action**: Open these files and keep them handy.

#### Step 5: Check What to Build (2 minutes)
📄 **Files**:
- `.kiro/specs/autocom/tasks.md` - Implementation tasks
- `.kiro/specs/autocom/design.md` - Component designs
- `.kiro/specs/autocom/requirements.md` - Requirements

**Action**: Browse these to understand what needs to be built.

---

## 🚨 The 5 Critical Rules (MEMORIZE THESE!)

### 1. Always Read Context Files First

Before coding ANYTHING, read:
```bash
.autocom-context.json      # Project metadata
.dev-context.yaml          # Development context
TYPES_INDEX.md             # All datatypes
FUNCTION_INDEX.md          # All functions
.kiro/specs/autocom/tasks.md  # What to implement
```

### 2. Always Use Existing Types

```python
# ✅ CORRECT: Use existing types
from core.orchestrator import Intent
from core.notification_hub import Notification, Priority
from agents.base_agent import BaseAgent, AgentConfig

# ❌ WRONG: Creating new types that already exist
class MyIntent:  # DON'T DO THIS!
    pass
```

**How to check**: Search `TYPES_INDEX.md` before creating any new type.

### 3. Always Follow Async-First

```python
# ✅ CORRECT: All I/O is async
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        return await session.get(url)

# ❌ WRONG: Blocking I/O
def fetch_data():
    return requests.get(url)  # BLOCKING!
```

**Rule**: If it does I/O (network, file, database), it MUST be async.

### 4. Always Use Event Bus

```python
# ✅ CORRECT: Communicate via event bus
await event_bus.emit("agent.response", {"data": result})

# ❌ WRONG: Direct calls
orchestrator.handle_response(result)  # DON'T!
```

**Rule**: Components NEVER call each other directly. Always use event bus.

### 5. Always Inherit from Base Classes

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

**Rule**: Always inherit from base classes. Check `agents/base_agent.py`.

---

## 📖 Coding Standards Cheat Sheet

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

## 🚫 Banned Patterns (NEVER USE!)

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

## 🎯 Your First Task

### Step 1: Pick a Task
```bash
# Open tasks file
cat .kiro/specs/autocom/tasks.md

# Find next task (e.g., "Implement Gmail Agent")
```

### Step 2: Read the Design
```bash
# Open design file
cat .kiro/specs/autocom/design.md

# Find relevant section (e.g., "Gmail Agent Design")
```

### Step 3: Check Existing Types
```bash
# Check what types exist
cat TYPES_INDEX.md | grep -i "agent"
```

### Step 4: Implement
```python
# Follow patterns from AGENT_CODING_RULES.md
# Use existing types from TYPES_INDEX.md
# Reference functions from FUNCTION_INDEX.md
```

### Step 5: Test
```bash
# Run tests
pytest tests/

# Check types
mypy .

# Format code
black .
```

### Step 6: Commit
```bash
# Commit with descriptive message
git add .
git commit -m "feat: implement Gmail agent authentication"
```

---

## ✅ Self-Check: Are You Ready?

Answer these questions:

- ✅ What is AUTOCOM? (Voice-first automation platform)
- ✅ What is FORGE? (Framework for building agent-based systems)
- ✅ What is the architecture? (Event-driven, async-first, agent-based)
- ✅ Where are the types? (TYPES_INDEX.md)
- ✅ Where are the tasks? (.kiro/specs/autocom/tasks.md)
- ✅ What's the coding style? (Python 3.10+, async-first, type hints)
- ✅ How do components communicate? (Event bus)
- ✅ What's banned? (Blocking I/O, direct calls, hardcoded values)

If you can answer all of these, you're ready to code! 🎉

---

## 📞 Getting Help

### Stuck on Something?

1. **Re-read** `rules/AGENT_CODING_RULES.md`
2. **Check** `TYPES_INDEX.md` for existing types
3. **Check** `FUNCTION_INDEX.md` for existing functions
4. **Look at** existing code in `core/` and `agents/`
5. **Review** `rules/Forge-Framework.md` for patterns

### Need Examples?

- **Agent example**: `agents/base_agent.py`
- **Event bus usage**: `core/orchestrator.py`
- **LLM usage**: `core/task_extractor.py`
- **Async patterns**: `core/event_bus.py`
- **Error handling**: `agents/base_agent.py`

---

## 🚀 Ready to Code!

You've completed the onboarding! Here's your action plan:

1. ✅ You understand AUTOCOM and FORGE
2. ✅ You know the 5 critical rules
3. ✅ You know the coding standards
4. ✅ You know what's banned
5. ✅ You have the quick reference
6. ✅ You know where to find help

**Now go build something amazing!** 🎉

---

## 📁 Essential Files Reference

### Must Read
- `rules/00-START-HERE.md` - Entry point
- `rules/AGENT_CODING_RULES.md` - Coding rules
- `.autocom-context.json` - Project metadata
- `TYPES_INDEX.md` - All datatypes
- `FUNCTION_INDEX.md` - All functions

### Specifications
- `.kiro/specs/autocom/requirements.md` - Requirements
- `.kiro/specs/autocom/design.md` - Designs
- `.kiro/specs/autocom/tasks.md` - Tasks

### Framework Documentation
- `FORGE_FRAMEWORK_SUMMARY.md` - Framework overview
- `FORGE_ENTERPRISE_FEATURES.md` - Enterprise features
- `rules/Forge-Framework.md` - Framework guide

### Quick Reference
- `QUICK_REFERENCE.md` - Quick reference
- `PROJECT_STATUS.md` - Current status
- `README.md` - Project overview

---

**Last Updated:** November 11, 2025  
**Version:** 2.0.0  
**Status:** Complete & Production-Ready  
**Compatible with:** ALL AI coding assistants

---

*Welcome to the team! Let's build AUTOCOM together.* 🚀
