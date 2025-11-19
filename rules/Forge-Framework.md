# FORGE Framework Rules - Universal AI Agent Guide

> **For ALL AI Coding Assistants: Kiro, Cursor, Windsurf, VS Code, GitHub Copilot, Cody, etc.**

---

## Overview

- **Framework Name:** FORGE (Framework for Orchestrated, Resilient, Generative Engines)
- **Purpose:** Python framework for building agentic, async-first, event-driven desktop applications
- **Philosophy:** Like Django for Web, FORGE is for Automation
- **Version:** 2.0 Enterprise Edition
- **Zero Project Coupling:** Pure framework rules—applicable to any FORGE-based project

---

## 1. Project Structure (Strictly Enforced)

```text
forge-app/
├── agents/              # Pluggable service integration agents
│   ├── __init__.py
│   ├── base_agent.py    # ABC: authenticate(), fetch(), act()
│   └── <service>_agent.py
│
├── core/                # Core framework runtime
│   ├── __init__.py
│   ├── orchestrator.py  # Intent classification & routing
│   ├── event_bus.py     # Async pub/sub messaging
│   ├── llm.py           # Local LLM integration
│   ├── main.py          # Application entry point
│   ├── middleware.py    # 🆕 Enterprise middleware system
│   ├── dependency_injection.py  # 🆕 DI container
│   ├── health_check.py  # 🆕 Health monitoring
│   └── circuit_breaker.py  # 🆕 Resilience patterns
│
├── ui/                  # Desktop UI layer (PyQt6/PySide6)
│   ├── __init__.py
│   ├── base_ui.py
│   └── dashboard.py
│
├── database/            # Local persistence
│   ├── __init__.py
│   ├── models.py
│   ├── connection.py
│   └── memory.py        # Memory store with embeddings
│
├── voice/               # Voice pipeline (optional)
│   ├── __init__.py
│   ├── wake_word.py
│   ├── stt.py
│   └── tts.py
│
├── config/              # Configuration
│   ├── config.yaml      # Main config
│   ├── agents.yaml      # Agent-specific config
│   └── .env.example     # Environment template
│
├── extensions/          # Plugin system
│   ├── __init__.py
│   └── loader.py
│
├── memory/              # Agent memory (context, types, logs)
│   ├── context.db       # SQLite: agent decisions
│   ├── types/           # .pyi type stubs
│   ├── docs/            # Function doc caches
│   ├── backups/         # State snapshots
│   └── agent_log.yaml   # Human-readable logs
│
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_core.py
│   └── test_integration.py
│
├── docs/                # Documentation
│   └── README.md
│
├── forge.toml           # FORGE framework configuration
├── pyproject.toml       # Python packaging
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

**IDE Actions:**
- Validate structure on project open
- `forge init <name>` scaffolds the full layout
- New files in `agents/` must inherit `BaseAgent`
- New files in `core/` must follow async-first patterns

---

## 2. FORGE CLI Commands

| Command | Action |
|---------|--------|
| `forge init <name>` | Scaffold complete application structure |
| `forge generate agent <name>` | Create new agent inheriting `BaseAgent` |
| `forge run` | Launch orchestrator and UI |
| `forge test` | Run test suite with coverage |
| `forge build` | Produce distributable (AppImage/exe) |
| `forge validate` | Validate project structure and config |

**IDE Integration:** Surface these commands in command palette

---

## 3. Global Coding Standards

| Rule | Enforcement |
|------|-------------|
| **Python Version** | 3.10+ (use modern features: match/case, union types) |
| **Linter** | `ruff` (line length 88, strict mode) |
| **Type Checking** | `mypy --strict` (no `Any` types) |
| **Async** | All I/O in `async def` functions |
| **Imports** | Absolute imports only (no relative) |
| **Banned APIs** | `threading`, `time.sleep()`, `requests`, `subprocess` |
| **Docstrings** | Google style required for all public functions |
| **Error Handling** | Specific exceptions, comprehensive logging |

---

## 4. Agent Base Template

All agents must inherit from `BaseAgent` in `agents/base_agent.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, List
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Agent configuration with validation."""
    name: str
    enabled: bool = True
    token: str = ""
    endpoint: str = ""
    timeout: int = 30


class BaseAgent(ABC):
    """Abstract base class for all FORGE agents."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with external service."""
        pass
    
    @abstractmethod
    async def fetch(self, params: dict) -> List[Dict]:
        """Fetch data from external source."""
        pass
    
    @abstractmethod
    async def act(self, action: str, data: dict) -> bool:
        """Execute action on external system."""
        pass
```

**IDE Rules:**
- Auto-insert config and async method stubs
- Suggest `tenacity.retry` for network calls
- Ensure exports in `agents/__init__.py`
- Validate Pydantic models on save

---

## 5. Core Orchestration Patterns

### Orchestrator (`core/orchestrator.py`)

```python
from typing import Dict, Optional
from core.event_bus import EventBus
from core.llm import LocalLLM


class Orchestrator:
    """Central intent classification and routing."""
    
    def __init__(self, event_bus: EventBus, llm: LocalLLM):
        self.event_bus = event_bus
        self.llm = llm
        self.agent_registry: Dict[str, BaseAgent] = {}
    
    async def process_input(self, user_input: str, context: list) -> None:
        """Process user input and route to appropriate agent."""
        # Classify intent using LLM
        intent = await self.llm.classify_intent(user_input, context)
        
        # Route to agent via event bus
        await self.event_bus.emit(
            f"agent.{intent.target}.{intent.action}",
            intent.parameters
        )
    
    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """Register agent for routing."""
        self.agent_registry[name] = agent
```

### Event Bus (`core/event_bus.py`)

```python
import asyncio
from typing import Callable, Dict, List


class EventBus:
    """Async pub/sub messaging system."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    async def emit(self, event: str, data: dict) -> None:
        """Emit event to all subscribers."""
        if event in self.subscribers:
            tasks = [handler(data) for handler in self.subscribers[event]]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe(self, event: str, handler: Callable) -> None:
        """Subscribe to event."""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)
```

**IDE Rules:**
- Disallow direct agent-to-agent calls—always use event bus
- Highlight async orchestration patterns
- Suggest event naming conventions: `<component>.<target>.<action>`

---

## 6. Enterprise Features (FORGE 2.0)

### Middleware System

```python
from core.middleware import create_production_stack

# Use middleware for all event processing
stack = create_production_stack()
result = await stack.execute(event, data, handler)
```

### Dependency Injection

```python
from core.dependency_injection import get_container, Scope

container = get_container()
container.register(EventBus, scope=Scope.SINGLETON)
container.register(BaseAgent, GmailAgent, scope=Scope.TRANSIENT)

# Resolve dependencies
event_bus = container.resolve(EventBus)
```

### Circuit Breaker

```python
from core.circuit_breaker import circuit_breaker

@circuit_breaker("gmail_api", failure_threshold=5)
async def fetch_emails():
    return await gmail_client.fetch()
```

### Health Checks

```python
from core.health_check import HealthCheckManager, DatabaseHealthCheck

health_manager = HealthCheckManager()
health_manager.register(DatabaseHealthCheck(db))

is_ready = await health_manager.check_readiness()
```

**See `FORGE_ENTERPRISE_FEATURES.md` for complete documentation.**

---

## 7. AI & Voice Pipeline (Optional)

| Component | Library | Rule |
|-----------|---------|------|
| **LLM** | `ollama` | Local-only inference (privacy-first) |
| **STT** | `openai-whisper` | Offline transcription |
| **TTS** | `pyttsx3` | Optional voice feedback |
| **Wake Word** | `porcupine2` | Configurable activation |

```python
# voice/pipeline.py
async def voice_loop():
    async with WakeWordDetector() as detector:
        while True:
            if await detector.detect():
                text = await stt.transcribe()
                intent = await llm.classify(text)
                await orchestrator.route(intent)
```

**IDE Suggestions:**
- Auto-wrap voice loops in `async with` context
- Suggest error handling for audio device failures
- Recommend offline-first patterns

---

## 8. UI Layer (PyQt6/PySide6)

```python
# ui/dashboard.py
from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon
from PyQt6.QtCore import QTimer


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_polling()
    
    def setup_polling(self):
        """Poll for updates every 30 seconds."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30 seconds
```

**IDE Rules:**
- Encourage `QTableView` and `QSystemTrayIcon` components
- Offer headless-mode fallbacks when UI unavailable
- Suggest async-safe Qt patterns (QThread, signals/slots)

---

## 9. Database & Memory

```python
# database/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LogEntry(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)
    payload = Column(String)
    timestamp = Column(DateTime, index=True)
```

**IDE Rules:**
- Auto-migrate schemas on application boot
- Index frequently queried fields
- Suggest SQLAlchemy async patterns for I/O

---

## 10. Memory Directory – Framework Brain

```text
memory/
├── context.db          # SQLite: agent decisions, state
├── types/              # .pyi type stubs for IDE
├── docs/               # Function doc caches
├── backups/            # State snapshots
└── agent_log.yaml      # Human-readable decision log
```

**IDE Must:**
- Log AI decisions for traceability
- Restore context when switching IDEs
- Sync memory/ via git LFS for large traces
- Encrypt sensitive data (tokens, credentials)

---

## 11. Configuration

### `config/config.yaml`

```yaml
app:
  name: "MyForgeApp"
  version: "1.0.0"

agents:
  gmail: "agents.gmail.GmailAgent"
  slack: "agents.slack.SlackAgent"

ai:
  model: "llama3.1:8b"
  local: true
  temperature: 0.7

voice:
  enabled: true
  wake_word: "hey-forge"
  stt_model: "whisper-base"
```

**IDE Rules:**
- Validate config using Pydantic before load
- Suggest agent paths as typed completions
- Hot-reload on config changes

---

## 12. Testing

```bash
# Run tests with coverage
pytest --cov=agents --cov=core --cov-report=html

# Type checking
mypy .

# Linting
ruff check .

# Formatting
black .
```

**IDE Rules:**
- Enforce ≥80% coverage targets
- Mock external APIs during test generation
- Auto-run tests on save (optional)
- Suggest test cases based on function signatures

---

## 13. Build & Deployment

```bash
# Build distributable
forge build  # Produces forge-app.AppImage (Linux)

# Or manually with PyInstaller
pyinstaller --onefile --windowed core/main.py
```

**IDE Rules:**
- Auto-generate PyInstaller spec when needed
- Include all dependencies in build
- Test build in clean environment

---

## 14. Framework Philosophy

| Principle | Enforcement |
|-----------|-------------|
| **Modular** | Agents function as plugins |
| **Async-First** | No blocking I/O in runtime |
| **Local-First** | Cloud services optional, not required |
| **Event-Driven** | Components communicate via event bus |
| **Extensible** | `forge generate` scaffolds new capabilities |
| **IDE-Aware** | Memory directory preserves context |
| **Enterprise-Ready** | Middleware, DI, health checks, circuit breakers |
| **Privacy-Focused** | Local LLM, encrypted storage, no cloud deps |

---

## 15. Common Patterns

### Pattern 1: Creating a New Agent

```python
from agents.base_agent import BaseAgent, AgentConfig
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

### Pattern 2: Event-Driven Communication

```python
# Subscribe to events
async def handle_agent_response(data: dict) -> None:
    logger.info(f"Agent response: {data}")

await event_bus.subscribe("agent.response", handle_agent_response)

# Emit events
await event_bus.emit("agent.gmail.fetch", {"unread_only": True})
```

### Pattern 3: Enterprise Request Pipeline

```python
from core.middleware import create_production_stack
from core.circuit_breaker import circuit_breaker
from core.dependency_injection import inject, get_container

# Setup
stack = create_production_stack()
container = get_container()
container.register(GmailAgent, scope=Scope.SINGLETON)

# Handler with DI and circuit breaker
@inject(container)
@circuit_breaker("gmail_fetch", failure_threshold=5)
async def fetch_handler(event: str, data: dict, agent: GmailAgent):
    return await agent.fetch(data)

# Execute through middleware
result = await stack.execute("fetch_emails", {}, fetch_handler)
```

---

## 16. Banned Patterns (NEVER USE!)

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

### ❌ Direct Agent Calls

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

# ALWAYS use config:
api_key = config.get("api_key")
```

---

## 17. IDE Integration

### Context Files

- `.autocom-context.json` - Project metadata
- `.dev-context.yaml` - Development context
- `memory/context.db` - Agent decision history

### Auto-Completions

- Agent paths from `config/agents.yaml`
- Event names from event bus registry
- Type hints from `memory/types/`

### Validation

- Structure check on project open
- Type check with mypy on save
- Lint with ruff on save
- Test on commit (optional)

---

## 18. Migration from Other Frameworks

### From Django

- Replace views with agents
- Replace URLs with event routing
- Replace ORM with SQLAlchemy (async)
- Keep middleware concept (FORGE has it!)

### From FastAPI

- Replace endpoints with agents
- Replace Pydantic models (keep them!)
- Replace dependency injection (FORGE has it!)
- Keep async patterns

### From Flask

- Replace routes with event handlers
- Add async support
- Add type hints
- Add enterprise features

---

## 19. Best Practices

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

## 20. Resources

### Documentation

- `FORGE_FRAMEWORK_SUMMARY.md` - Framework overview
- `FORGE_ENTERPRISE_FEATURES.md` - Enterprise features
- `TYPES_INDEX.md` - All datatypes
- `FUNCTION_INDEX.md` - All functions
- `QUICK_REFERENCE.md` - Quick reference

### Examples

- `agents/base_agent.py` - Agent template
- `core/orchestrator.py` - Orchestration patterns
- `core/event_bus.py` - Event-driven patterns
- `core/middleware.py` - Middleware patterns

---

*Use these rules with FORGE to build production-ready, agent-based automation systems that work seamlessly across all AI coding assistants.*

---

**Last Updated:** November 11, 2025  
**Version:** 2.0.0 Enterprise Edition  
**Compatible with:** ALL AI coding assistants (Kiro, Cursor, Windsurf, VS Code, GitHub Copilot, Cody, Tabnine, etc.)
