# 🔧 Technical Design Document

## 1. Module Structure

```
autocom/
├── core/                    # Core application logic
│   ├── orchestrator.py      # Command processing
│   ├── event_bus.py         # Pub/sub messaging
│   ├── llm.py               # LLM integration
│   ├── notification_hub.py  # Notification management
│   ├── task_extractor.py    # Task detection
│   ├── draft_manager.py     # Draft generation
│   ├── learning_engine.py   # Preference learning
│   ├── sentiment_analyzer.py# Sentiment detection
│   └── main.py              # Entry point
│
├── agents/                  # External service integrations
│   ├── base_agent.py        # Abstract base class
│   ├── gmail_agent.py       # Gmail integration
│   └── slack_agent.py       # Slack integration
│
├── voice/                   # Voice pipeline
│   ├── wake_detector.py     # Wake word detection
│   ├── speech_to_text.py    # STT processing
│   └── text_to_speech.py    # TTS processing
│
├── ui/                      # User interface
│   ├── main_window.py       # Main dashboard
│   ├── message_list.py      # Message list widget
│   ├── message_detail.py    # Message detail widget
│   ├── settings_panel.py    # Settings UI
│   ├── notification_popup.py# Pop-up notifications
│   └── system_tray.py       # Tray icon
│
├── database/                # Data persistence
│   ├── db_manager.py        # Database operations
│   └── models.py            # Data models
│
├── algorithms/              # Custom algorithms
│   ├── priority_scorer.py   # Priority calculation
│   ├── intent_classifier.py # Intent parsing
│   └── context_matcher.py   # Context matching
│
└── config/                  # Configuration
    ├── config.yaml          # Main config
    └── agents.yaml          # Agent settings
```

---

## 2. Core Classes

### 2.1 Orchestrator
```python
class Orchestrator:
    """Central command processor."""
    
    def __init__(self, llm, event_bus, memory):
        self.llm = llm
        self.event_bus = event_bus
        self.memory = memory
    
    async def process_command(self, text: str) -> None:
        """Process user command."""
        # 1. Classify intent
        intent = await self.classify_intent(text)
        
        # 2. Route to handler
        await self.route_intent(intent)
    
    async def classify_intent(self, text: str) -> Intent:
        """Classify user intent using LLM."""
        pass
    
    async def route_intent(self, intent: Intent) -> None:
        """Route intent to appropriate agent."""
        pass
```

### 2.2 Event Bus
```python
class EventBus:
    """Async pub/sub messaging."""
    
    def __init__(self):
        self.subscribers = {}
        self.queue = asyncio.Queue()
    
    async def emit(self, event: str, data: dict) -> None:
        """Publish event."""
        await self.queue.put((event, data))
    
    async def subscribe(self, event: str, handler: Callable) -> None:
        """Subscribe to event."""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)
    
    async def start(self) -> None:
        """Start processing events."""
        while True:
            event, data = await self.queue.get()
            for handler in self.subscribers.get(event, []):
                await handler(data)
```

### 2.3 Base Agent
```python
class BaseAgent(ABC):
    """Abstract base for all agents."""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with service."""
        pass
    
    @abstractmethod
    async def fetch(self, params: dict) -> list:
        """Fetch data from service."""
        pass
    
    @abstractmethod
    async def send(self, data: dict) -> bool:
        """Send data to service."""
        pass
```

---

## 3. Data Models

### 3.1 Message
```python
@dataclass
class Message:
    id: str
    source: str          # "gmail" or "slack"
    sender: str
    subject: str         # For emails
    content: str
    timestamp: datetime
    priority: Priority
    read: bool = False
```

### 3.2 Task
```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    source_message_id: str
    deadline: Optional[datetime]
    completed: bool = False
```

### 3.3 Intent
```python
@dataclass
class Intent:
    action: str          # "fetch", "send", etc.
    target: str          # "gmail", "slack"
    parameters: dict
    confidence: float
    raw_input: str
```

### 3.4 Notification
```python
@dataclass
class Notification:
    id: str
    title: str
    body: str
    priority: Priority
    source: str
    timestamp: datetime
    actions: list[str]
```

---

## 4. API Interfaces

### 4.1 Gmail Agent Interface
```python
class GmailAgent(BaseAgent):
    async def authenticate(self) -> bool
    async def fetch(self, params: dict) -> list[Message]
    async def send(self, data: dict) -> bool
    async def mark_read(self, message_id: str) -> bool
    async def archive(self, message_id: str) -> bool
```

### 4.2 Slack Agent Interface
```python
class SlackAgent(BaseAgent):
    async def authenticate(self) -> bool
    async def fetch(self, params: dict) -> list[Message]
    async def send(self, data: dict) -> bool
    async def set_status(self, status: str) -> bool
    async def start_realtime(self) -> None
```

---

## 5. Event Types

| Event | Data | Description |
|-------|------|-------------|
| `message.new` | Message | New message received |
| `message.read` | message_id | Message marked read |
| `task.created` | Task | New task extracted |
| `task.completed` | task_id | Task completed |
| `notification.show` | Notification | Show notification |
| `voice.command` | text | Voice command received |
| `voice.speak` | text | Speak text via TTS |

---

## 6. Configuration

### 6.1 Main Config (config.yaml)
```yaml
app:
  name: AUTOCOM
  version: 1.0.0

llm:
  model: llama3.1:8b
  endpoint: http://localhost:11434

voice:
  wake_word: hey-auto
  enabled: true

notifications:
  quiet_hours:
    enabled: true
    start: "22:00"
    end: "08:00"

database:
  path: data/autocom.db
  prune_days: 30
```

### 6.2 Agent Config (agents.yaml)
```yaml
gmail:
  enabled: true
  credentials_file: config/gmail_credentials.json
  scopes:
    - gmail.readonly
    - gmail.send

slack:
  enabled: true
  token_file: config/slack_token.json
  realtime: true
```

---

## 7. Error Handling

### 7.1 Exception Hierarchy
```python
class AutocomError(Exception):
    """Base exception."""
    pass

class AuthenticationError(AutocomError):
    """Authentication failed."""
    pass

class NetworkError(AutocomError):
    """Network request failed."""
    pass

class LLMError(AutocomError):
    """LLM processing failed."""
    pass
```

### 7.2 Error Recovery
| Error | Recovery |
|-------|----------|
| Auth failed | Prompt re-authentication |
| Network error | Retry with backoff |
| LLM error | Fallback to rule-based |
| Voice error | Ask to repeat |

---

## 8. Security Design

### 8.1 Token Storage
- OAuth tokens encrypted with AES-256
- Stored in local encrypted file
- Never transmitted externally

### 8.2 Data Privacy
- All AI processing local
- No telemetry
- User can delete all data

### 8.3 Input Validation
- All inputs sanitized
- SQL injection prevention
- XSS prevention in UI
