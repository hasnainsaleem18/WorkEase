# AUTOCOM

> **"Automate Everything. From Voice to Victory."**  
> **100% AI Agent Friendly** - Works with Kiro, Cursor, Windsurf, VS Code, GitHub Copilot, and ALL AI assistants

AUTOCOM is a voice-first, local-LLM-powered automation platform built on the **FORGE Framework**. It unifies communication and task management tools (Gmail, Slack, Jira) through an intelligent orchestrator that routes user intents to specialized sub-agents.

## 🤖 For AI Agents: Quick Start

**New to this project?** Start here:

1. 📄 **Read First**: `rules/00-START-HERE.md` (5 min) - Your entry point
2. 📄 **Coding Rules**: `rules/AGENT_CODING_RULES.md` (20 min) - Essential rules
3. 📄 **Onboarding**: `AI_AGENT_ONBOARDING.md` (30 min) - Complete guide
4. 📄 **Types**: `TYPES_INDEX.md` - All datatypes (use these!)
5. 📄 **Tasks**: `.kiro/specs/autocom/tasks.md` - What to build

**IDE-Specific Rules**:
- Cursor: `.cursorrules`
- Windsurf: `.windsurfrules`
- GitHub Copilot: `.github/copilot-instructions.md`
- VS Code: `.cursorrules` (compatible)

**Critical Rules**: Always use existing types, follow async-first, use event bus, inherit from base classes, no blocking I/O!

## 🎯 Key Features

- **Voice-First Interface**: Wake word activation ("Hey Auto") with natural language commands
- **Local LLM**: Privacy-focused AI using Ollama (Llama 3.1 8B) - no cloud required
- **Unified Inbox**: Aggregate Gmail and Slack messages in one place
- **Smart Automation**: Auto-extract tasks from messages and create Jira tickets
- **Native Desktop**: True native application built with PyQt6 (not a web wrapper)
- **Cross-Platform**: Linux-first with Windows and macOS support
- **Extensible**: Plugin-based agent system for easy service integration

## 🏗️ Architecture

AUTOCOM is built on the **FORGE Framework** - a Python-native, async-first framework for agentic applications.

```
┌─────────────────────────────────────┐
│   Voice Pipeline (Wake/STT/TTS)    │
│   Desktop UI (PyQt6)                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Orchestrator (Local LLM)          │
│   - Intent Classification           │
│   - Agent Routing                   │
│   - Context Management              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Event Bus (Async Pub/Sub)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Agents (Gmail, Slack, Jira)       │
│   - OAuth2 Authentication           │
│   - API Integration                 │
│   - Action Execution                │
└─────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Ollama**: For local LLM inference
- **OS**: Linux (Ubuntu 20.04+, Fedora 35+), Windows 10+, or macOS 11+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB (includes LLM model)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd autocom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama and Model

```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the LLM model
# For standard PCs (8GB+ RAM):
ollama pull llama3.1:8b

# For weak PCs (4-6GB RAM):
ollama pull llama3.2:3b
# OR
ollama pull phi3:mini
# OR (very weak PCs):
ollama pull tinyllama
```

**Model Selection Guide**:
- `llama3.1:8b` (4.7GB) - Best quality, needs 8GB+ RAM
- `llama3.2:3b` (2GB) - Good balance, works on 4-6GB RAM
- `phi3:mini` (2.3GB) - Microsoft's efficient model
- `tinyllama` (637MB) - Fastest, minimal RAM, basic quality

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API credentials
nano .env
```

### 4. Run AUTOCOM

```bash
# Start the application
python -m core.main
```

## 📁 Project Structure

```
autocom/
├── agents/              # Service-specific agents
│   ├── base_agent.py    # Abstract base class
│   ├── gmail/           # Gmail integration
│   ├── slack/           # Slack integration
│   └── jira/            # Jira integration
├── core/                # Core framework
│   ├── orchestrator.py  # Intent router
│   ├── event_bus.py     # Async messaging
│   ├── llm.py           # LLM interface
│   └── main.py          # Entry point
├── database/            # Data persistence
│   └── memory.py        # SQLite + embeddings
├── voice/               # Voice pipeline
│   ├── wake.py          # Wake word detection
│   ├── stt.py           # Speech-to-text
│   └── tts.py           # Text-to-speech
├── ui/                  # PyQt6 desktop UI
│   ├── dashboard.py     # Main window
│   ├── settings.py      # Configuration
│   └── tray.py          # System tray
├── config/              # Configuration files
│   ├── config.yaml      # Main config
│   └── agents.yaml      # Agent settings
├── memory/              # Runtime data
│   └── context.db       # Conversation history
├── tests/               # Test suite
└── docs/                # Documentation
```

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)

```yaml
orchestrator:
  llm_model: "llama3.1:8b"
  confidence_threshold: 0.7

voice:
  wake_word: "hey-auto"
  enabled: true

notifications:
  quiet_hours:
    enabled: true
    start: "22:00"
    end: "08:00"
```

### Agent Configuration (`config/agents.yaml`)

```yaml
agents:
  gmail:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/gmail.readonly"
      - "https://www.googleapis.com/auth/gmail.send"
  
  slack:
    enabled: true
    realtime: true
  
  jira:
    enabled: true
    server: "https://your-domain.atlassian.net"
```

## 🎤 Voice Commands

```
"Hey Auto, check my emails"
"Hey Auto, send a message to John on Slack"
"Hey Auto, create a Jira ticket for bug fix"
"Hey Auto, summarize my inbox"
```

## 🧪 Development

### Run Tests

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

### Build Distribution

```bash
# Build AppImage (Linux)
./build.sh

# Output: autocom.AppImage
```

## 🔐 Security

- **Local-First**: All AI inference happens on-device
- **Encrypted Storage**: OAuth tokens encrypted with AES-256
- **No Telemetry**: Zero data transmission to external servers
- **Secure by Default**: Input validation and parameterized queries

## 📚 Documentation

### Core Specifications
- [Requirements](/.kiro/specs/autocom/requirements.md) - 25 detailed requirements
- [Design Document](/.kiro/specs/autocom/design.md) - Complete architecture
- [Implementation Plan](/.kiro/specs/autocom/tasks.md) - Step-by-step tasks
- [FORGE Framework](/Forge-Framework.md) - Framework documentation

### Guides & References
- [Architecture Summary](/.kiro/specs/autocom/ARCHITECTURE_SUMMARY.md) - **Start here!**
- [Model Selection Guide](/docs/MODEL_SELECTION.md) - Choose the right LLM for your PC
- [LangChain/RAG Upgrade Guide](/.kiro/specs/autocom/LANGCHAIN_RAG_UPGRADE.md) - Future enhancements

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built on the **FORGE Framework**
- Powered by **Ollama** and **Llama 3.1**
- UI built with **PyQt6**
- Voice powered by **Porcupine**, **Whisper**, and **Piper**

---

**Made with ❤️ for automation enthusiasts**
