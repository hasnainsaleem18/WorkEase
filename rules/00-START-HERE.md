# 🚀 START HERE - AI Agent Onboarding Guide

> **Welcome! This is your entry point to the AUTOCOM project.**  
> **Read this first, then follow the links to dive deeper.**

---

## 🎯 What is AUTOCOM?

**AUTOCOM** is a voice-first automation platform built on the **FORGE Framework**. It's like having a personal AI assistant that:

- Monitors your Gmail and Slack
- Generates draft replies
- Extracts tasks from messages
- Provides daily summaries
- Responds to voice commands
- Learns your preferences over time

**Status:** 50% complete (specs & framework done, agents & UI to implement)

---

## 📚 Quick Navigation (Read in Order)

### 1. **Project Overview** (5 minutes)
- 📄 `../README.md` - Project description and features
- 📄 `../.autocom-context.json` - Project metadata
- 📄 `../.dev-context.yaml` - Development context

### 2. **Coding Rules** (20 minutes) ⭐ **MOST IMPORTANT**
- 📄 `AGENT_CODING_RULES.md` - **START HERE FOR CODING!**
- 📄 `Forge-Framework.md` - Framework architecture and patterns
- 📄 `MIND-Model-Rules.md` - Development methodology

### 3. **Project Structure** (10 minutes)
- 📄 `../TYPES_INDEX.md` - All datatypes (use these!)
- 📄 `../FUNCTION_INDEX.md` - All functions (reference these!)
- 📄 `../PROJECT_TREE.md` - Complete file structure

### 4. **What to Build** (15 minutes)
- 📄 `../.kiro/specs/autocom/requirements.md` - 25 requirements
- 📄 `../.kiro/specs/autocom/design.md` - 17 component designs
- 📄 `../.kiro/specs/autocom/tasks.md` - 20 implementation tasks

### 5. **Framework Documentation** (10 minutes)
- 📄 `../FORGE_FRAMEWORK_SUMMARY.md` - Framework overview
- 📄 `../FORGE_ENTERPRISE_FEATURES.md` - Enterprise features
- 📄 `../QUICK_REFERENCE.md` - Quick reference guide

---

## 🎓 Learning Paths

### For First-Time Contributors (60 minutes)

1. **Read this file** (5 min)
2. **Read `AGENT_CODING_RULES.md`** (20 min) ⭐
3. **Browse `../TYPES_INDEX.md`** (5 min)
4. **Read `../.kiro/specs/autocom/design.md`** (15 min)
5. **Pick a task from `../.kiro/specs/autocom/tasks.md`** (5 min)
6. **Start coding!** (∞ min)

### For Experienced Developers (20 minutes)

1. **Skim `AGENT_CODING_RULES.md`** (5 min)
2. **Check `../TYPES_INDEX.md`** (3 min)
3. **Review task in `../.kiro/specs/autocom/tasks.md`** (2 min)
4. **Check design in `../.kiro/specs/autocom/design.md`** (5 min)
5. **Start coding!** (∞ min)

### For AI Agents (10 minutes)

1. **Load `AGENT_CODING_RULES.md`** into context (2 min)
2. **Load `../TYPES_INDEX.md`** into context (2 min)
3. **Load current task from `../.kiro/specs/autocom/tasks.md`** (2 min)
4. **Load relevant design from `../.kiro/specs/autocom/design.md`** (2 min)
5. **Start coding!** (∞ min)

---

## 🏗️ Project Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│                    Voice Interface                       │
│              (Wake Word → STT → TTS)                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Orchestrator                            │
│         (Intent Classification & Routing)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Event Bus                               │
│            (Async Pub/Sub Messaging)                     │
└─────┬──────────┬──────────┬──────────┬─────────────────┘
      │          │          │          │
┌─────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│ Gmail   │ │ Slack  │ │ Draft  │ │ Task   │
│ Agent   │ │ Agent  │ │ Manager│ │Extract │
└─────────┘ └────────┘ └────────┘ └────────┘
      │          │          │          │
┌─────▼──────────▼──────────▼──────────▼─────────────────┐
│              Memory Store (SQLite + Embeddings)         │
└─────────────────────────────────────────────────────────┘
      │
┌─────▼─────────────────────────────────────────────────┐
│                Desktop UI (PyQt6)                      │
└───────────────────────────────────────────────────────┘
```

---

## 🔑 Key Concepts

### 1. **FORGE Framework**
- Python framework for building agent-based automation systems
- Like Django for web, FORGE is for automation
- Event-driven, async-first, modular architecture

### 2. **Agents**
- Pluggable components that integrate with external services
- All inherit from `BaseAgent`
- Communicate via event bus (no direct calls!)

### 3. **Event Bus**
- Central async pub/sub messaging system
- All components communicate through events
- Enables loose coupling and scalability

### 4. **Orchestrator**
- Central brain that classifies user intent
- Routes commands to appropriate agents
- Uses local LLM for natural language understanding

### 5. **MIND-Model**
- Non-linear development methodology
- Interconnected phases (requirements ↔ design ↔ coding ↔ testing)
- Supports parallel development and feedback loops

---

## 📋 Critical Rules (NEVER VIOLATE!)

### 1. **Always Read Context Files First**
```bash
# Before coding, read these:
.autocom-context.json
.dev-context.yaml
TYPES_INDEX.md
FUNCTION_INDEX.md
.kiro/specs/autocom/tasks.md
```

### 2. **Always Use Existing Types**
```python
# ✅ CORRECT: Use existing types
from core.orchestrator import Intent
from core.notification_hub import Notification, Priority

# ❌ WRONG: Creating new types that already exist
class MyIntent:  # DON'T DO THIS!
    pass
```

### 3. **Always Follow Async-First**
```python
# ✅ CORRECT: All I/O is async
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        return await session.get(url)

# ❌ WRONG: Blocking I/O
def fetch_data():
    return requests.get(url)  # BLOCKING!
```

### 4. **Always Use Event Bus**
```python
# ✅ CORRECT: Communicate via event bus
await event_bus.emit("agent.response", {"data": result})

# ❌ WRONG: Direct calls
orchestrator.handle_response(result)  # DON'T!
```

### 5. **Always Inherit from Base Classes**
```python
# ✅ CORRECT: Inherit from BaseAgent
class GmailAgent(BaseAgent):
    async def authenticate(self) -> bool:
        pass

# ❌ WRONG: Creating agents from scratch
class GmailAgent:  # Missing BaseAgent!
    pass
```

---

## 🎯 Current Status

### ✅ Completed (50%)

- **Specifications** (100%)
  - Requirements document (25 requirements)
  - Design document (17 components)
  - Tasks document (20 tasks)

- **Core Framework** (100%)
  - Orchestrator
  - Event Bus
  - Local LLM
  - Notification Hub
  - Task Extractor
  - Draft Manager
  - Learning Engine
  - Sentiment Analyzer
  - Digest Generator
  - Multi-Agent Coordinator

- **Enterprise Features** (100%)
  - Middleware System
  - Dependency Injection
  - Health Checks
  - Circuit Breaker

- **Database** (100%)
  - Memory Store (SQLite + embeddings)

- **Configuration** (100%)
  - Config files
  - Agent configs

### ⏳ To Implement (50%)

- **Agents** (0%)
  - Gmail Agent
  - Slack Agent

- **Voice Pipeline** (0%)
  - Wake Word Detection
  - Speech-to-Text
  - Text-to-Speech

- **Desktop UI** (0%)
  - Main Window
  - System Tray
  - Notifications

- **Integration & Testing** (0%)
  - Wire components together
  - End-to-end tests
  - Performance optimization

---

## 🛠️ Development Workflow

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

## 📞 Getting Help

### For AI Agents

- **Stuck?** Re-read `AGENT_CODING_RULES.md`
- **Need types?** Check `../TYPES_INDEX.md`
- **Need functions?** Check `../FUNCTION_INDEX.md`
- **Need examples?** Check existing code in `../core/` and `../agents/`
- **Need patterns?** Check `Forge-Framework.md`

### For Humans

- **Overview?** Read `../README.md`
- **Status?** Check `../PROJECT_STATUS.md`
- **Quick help?** Read `../QUICK_REFERENCE.md`
- **Framework?** Read `../FORGE_FRAMEWORK_SUMMARY.md`

---

## 🎉 Success Criteria

You're ready to code if you can answer:

- ✅ What is AUTOCOM? (Voice-first automation platform)
- ✅ What is FORGE? (Framework for building agent-based systems)
- ✅ What is the architecture? (Event-driven, async-first, agent-based)
- ✅ Where are the types? (TYPES_INDEX.md)
- ✅ Where are the tasks? (.kiro/specs/autocom/tasks.md)
- ✅ What's the coding style? (Python 3.10+, async-first, type hints)
- ✅ How do components communicate? (Event bus)
- ✅ What's banned? (Blocking I/O, direct calls, hardcoded values)

---

## 🚀 Ready to Code?

1. **Read `AGENT_CODING_RULES.md`** (20 minutes)
2. **Pick a task from `../.kiro/specs/autocom/tasks.md`**
3. **Start coding!**

**Remember:** Follow the rules, use existing types, and communicate via event bus. You've got this! 🎉

---

**Last Updated:** November 11, 2025  
**Version:** 2.0.0  
**Status:** Complete & Production-Ready  
**Compatible with:** ALL AI coding assistants

---

## 📁 Rules Directory Structure

```
rules/
├── 00-START-HERE.md              ⭐ YOU ARE HERE
├── README.md                      📖 Rules directory guide
├── AGENT_CODING_RULES.md          🤖 Universal coding rules (READ THIS!)
├── Forge-Framework.md             🏗️ Framework architecture
├── MIND-Model-Rules.md            🎯 Development methodology
├── MIND-Model-Context-Rules.md    💾 Context preservation
├── Cross-Platform-Rules.md        🌐 Cross-platform development
├── General-Dev-Rules.md           🛠️ General best practices
├── Framework.yaml                 📋 Machine-readable framework rules
├── MIND-Model-Rules.yaml          📋 Machine-readable MIND-Model rules
├── MIND-Model-Context.yaml        📋 Machine-readable context rules
├── Development-Rules.yaml         📋 Machine-readable dev rules
├── General-Development-Rules.yaml 📋 Machine-readable general rules
└── validate_rules.py              🔧 Rule validation script
```

---

*Welcome to AUTOCOM! Let's build something amazing together.* 🚀
