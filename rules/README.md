# 📖 Rules Directory - Complete Guide for AI Agents

> **Universal rules for ALL AI coding assistants working on AUTOCOM**

## 🎯 Purpose

This directory contains **comprehensive rules** that make AUTOCOM **100% agent-friendly** for ANY AI coding assistant:
- ✅ Kiro ✅ Cursor ✅ Windsurf ✅ VS Code Copilot ✅ GitHub Copilot ✅ Cody ✅ Tabnine ✅ Any AI assistant

---

## 📁 Files Overview

### 🚀 **START HERE** (Most Important!)

#### 0. **00-START-HERE.md** 🆕 ⭐⭐⭐
**Purpose**: Your entry point to the entire project  
**Read First**: ABSOLUTELY YES!  
**Contains**:
- Quick navigation guide
- Learning paths for different experience levels
- High-level architecture overview
- Critical rules summary
- Current project status
- Development workflow
- Success criteria

**When to use**: ALWAYS read this FIRST before anything else!

#### 1. **AGENT_CODING_RULES.md** 🆕 ⭐⭐
**Purpose**: Universal coding rules for ALL AI agents  
**Read Second**: YES!  
**Contains**:
- Project structure
- Critical rules (NEVER violate!)
- Coding standards
- Enterprise features usage
- Common patterns
- Banned patterns
- Quick reference

**When to use**: ALWAYS read this before coding anything!

---

### 🏗️ Framework Rules

#### 2. **Forge-Framework.md**
**Purpose**: FORGE Framework architecture and patterns  
**Contains**:
- Framework philosophy
- Project structure
- Agent base template
- Core orchestration patterns
- AI & voice pipeline
- Database patterns
- Testing guidelines

**When to use**: When implementing framework components

#### 3. **Framework.yaml**
**Purpose**: Machine-readable framework rules  
**Contains**:
- Structured framework configuration
- Validation rules
- Component specifications

**When to use**: For automated validation

---

### 🎯 MIND-Model Methodology

#### 4. **MIND-Model-Rules.md**
**Purpose**: MIND-Model SDLC methodology  
**Contains**:
- Core nodes (Requirements, Design, Coding, Testing, Deployment, Maintenance)
- Extended nodes (Security, Documentation, Operations, UX, Feedback)
- Enterprise nodes (Performance, Compliance, Architecture Review, etc.)
- Connection rules
- Flow & execution
- AI integration (Central, Distributed, Hybrid)
- Governance

**When to use**: Understanding project methodology

#### 5. **MIND-Model-Context-Rules.md**
**Purpose**: Context preservation across IDEs  
**Contains**:
- Session state management
- IDE switching
- Project understanding
- Development flow
- Context synchronization

**When to use**: When switching IDEs or preserving context

#### 6. **MIND-Model-Rules.yaml** & **MIND-Model-Context.yaml**
**Purpose**: Machine-readable MIND-Model rules  
**When to use**: For automated validation

---

### 🌐 Cross-Platform Development

#### 7. **Cross-Platform-Rules.md**
**Purpose**: Rules for Linux/Windows/macOS compatibility  
**Contains**:
- Scalability principles
- Cross-platform abstractions
- Packaging guidelines (PyInstaller, AppImage)
- Issue coverage (security, performance, accessibility)
- Testing strategies

**When to use**: When writing platform-specific code

---

### 🛠️ General Development

#### 8. **General-Dev-Rules.md**
**Purpose**: General development best practices  
**Contains**:
- Context management
- Project understanding
- Development flow
- Collaboration
- Governance
- Performance monitoring

**When to use**: General development guidance

#### 9. **Development-Rules.yaml** & **General-Development-Rules.yaml**
**Purpose**: Machine-readable development rules  
**When to use**: For automated validation

---

### 🔧 Utilities

#### 10. **validate_rules.py**
**Purpose**: Validate rule files  
**Usage**: `python rules/validate_rules.py`

---

## 🚀 Quick Start for AI Agents

### Step 1: Read Core Rules (5 minutes)
```bash
1. rules/AGENT_CODING_RULES.md  # ⭐ START HERE!
2. ../.autocom-context.json      # Project metadata
3. ../.dev-context.yaml          # Development context
```

### Step 2: Understand Project (10 minutes)
```bash
4. ../README.md                  # Project overview
5. ../TYPES_INDEX.md             # All datatypes
6. ../FUNCTION_INDEX.md          # All functions
```

### Step 3: Check What to Build (5 minutes)
```bash
7. ../.kiro/specs/autocom/tasks.md      # Implementation tasks
8. ../.kiro/specs/autocom/design.md     # Component designs
9. ../.kiro/specs/autocom/requirements.md # Requirements
```

### Step 4: Start Coding! 🎉
- Follow patterns in `AGENT_CODING_RULES.md`
- Use existing types from `TYPES_INDEX.md`
- Reference functions from `FUNCTION_INDEX.md`
- Check design in `design.md`
- Implement task from `tasks.md`

---

## 📊 Rule Priority

When rules conflict, follow this priority:

1. **AGENT_CODING_RULES.md** (Highest priority) ⭐
2. **Forge-Framework.md**
3. **MIND-Model-Rules.md**
4. **Cross-Platform-Rules.md**
5. **General-Dev-Rules.md**

---

## 🎯 Rule Categories

### Critical Rules (NEVER VIOLATE!)
- Always read context files first
- Always use existing types
- Always follow async-first
- Always use event bus
- Always inherit from base classes

### Coding Standards (STRICT!)
- Python 3.10+
- Full type hints
- Google-style docstrings
- Absolute imports only
- Comprehensive error handling

### Enterprise Features (USE THEM!)
- Middleware system
- Dependency injection
- Circuit breaker
- Health checks

### Banned Patterns (NEVER USE!)
- Blocking I/O (time.sleep, requests, threading)
- Direct agent-to-agent calls
- Hardcoded values
- Relative imports
- Bare except clauses

---

## 📚 Learning Path

### For New AI Agents (30 minutes total)
1. Read `AGENT_CODING_RULES.md` (20 min)
2. Read `.dev-context.yaml` (5 min)
3. Browse `TYPES_INDEX.md` (5 min)
4. Start coding! (∞ min)

### For Experienced AI Agents (10 minutes total)
1. Quick scan `AGENT_CODING_RULES.md` (5 min)
2. Check `tasks.md` for current task (2 min)
3. Reference `TYPES_INDEX.md` as needed (3 min)
4. Code with confidence! (∞ min)

---

## 🔍 Finding Information

### "Where do I find...?"

| What | Where |
|------|-------|
| Coding rules | `AGENT_CODING_RULES.md` |
| All datatypes | `../TYPES_INDEX.md` |
| All functions | `../FUNCTION_INDEX.md` |
| What to implement | `../.kiro/specs/autocom/tasks.md` |
| How to implement | `../.kiro/specs/autocom/design.md` |
| Why to implement | `../.kiro/specs/autocom/requirements.md` |
| Project overview | `../README.md` |
| Quick reference | `../QUICK_REFERENCE.md` |
| Framework docs | `../FORGE_FRAMEWORK_SUMMARY.md` |
| Enterprise features | `../FORGE_ENTERPRISE_FEATURES.md` |
| MIND-Model docs | `../MIND_MODEL_ENTERPRISE.md` |

---

## ✅ Validation

### Validate Your Code

```bash
# Type checking
mypy .

# Linting
ruff check .

# Formatting
black .

# Tests
pytest

# Coverage
pytest --cov=.
```

### Validate Rules

```bash
python rules/validate_rules.py
```

---

## 🎓 Best Practices

### DO ✅
- Read context files before coding
- Use existing types and functions
- Follow async-first architecture
- Use event bus for communication
- Inherit from base classes
- Add comprehensive error handling
- Add logging
- Write tests
- Update documentation

### DON'T ❌
- Use blocking I/O
- Make direct component calls
- Hardcode values
- Use relative imports
- Use bare except clauses
- Skip type hints
- Skip docstrings
- Skip error handling

---

## 🚀 Success Metrics

Your code is agent-friendly if:
- ✅ Any AI can understand the project in <30 minutes
- ✅ Any AI can start coding in <5 minutes
- ✅ Code follows all rules automatically
- ✅ No ambiguity in requirements
- ✅ Clear patterns to follow
- ✅ Comprehensive examples
- ✅ Complete documentation

**AUTOCOM achieves ALL of these!** 🎉

---

## 📞 Support

### For AI Agents
- Stuck? Read `AGENT_CODING_RULES.md` again
- Need types? Check `../TYPES_INDEX.md`
- Need functions? Check `../FUNCTION_INDEX.md`
- Need examples? Check existing code in `../core/` and `../agents/`

### For Humans
- Review `../README.md` in project root
- Check `../PROJECT_STATUS.md` for current state
- Read `../QUICK_REFERENCE.md` for quick help

---

## 🎉 Summary

This rules directory makes AUTOCOM **100% agent-friendly** by providing:

1. ✅ **Universal rules** for all AI assistants
2. ✅ **Clear patterns** to follow
3. ✅ **Comprehensive examples**
4. ✅ **Complete documentation**
5. ✅ **Validation tools**
6. ✅ **Quick reference**
7. ✅ **Learning paths**
8. ✅ **Best practices**

**Any AI agent can code on AUTOCOM with confidence!** 🚀

---

*Last Updated: November 11, 2025*  
*Version: 2.0.0*  
*Status: Complete & Production-Ready*  
*Compatible with: ALL AI coding assistants*
