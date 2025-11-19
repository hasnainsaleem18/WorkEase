# AUTOCOM Type Index

> Complete reference of all datatypes, classes, and interfaces in the project

## Core Types

### Intent (`core/orchestrator.py`)
```python
@dataclass
class Intent:
    action: str              # "fetch", "send", "create", "summarize"
    target: str              # "gmail", "slack", "jira"
    parameters: dict[str, Any]
    confidence: float        # 0.0-1.0
    context_id: str
    raw_input: str
```

### Notification (`core/notification_hub.py`)
```python
class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationType(str, Enum):
    MESSAGE = "message"
    ALERT = "alert"
    REMINDER = "reminder"
    DIGEST = "digest"
    SYSTEM = "system"

@dataclass
class Notification:
    id: str
    title: str
    body: str
    priority: Priority
    notification_type: NotificationType
    source: str              # "gmail", "slack", "system"
    timestamp: datetime
    actions: list[str]       # ["reply", "ignore", "mark_read"]
    metadata: dict[str, Any]
```

### Task (`core/task_extractor.py`)
```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: str            # "low", "normal", "high", "urgent"
    source: str              # "gmail", "slack"
    source_message_id: str
    source_sender: str
    extracted_at: datetime
    completed: bool = False
    due_date: Optional[datetime] = None
```

### EmailDraft (`core/draft_manager.py`)
```python
@dataclass
class EmailDraft:
    id: str
    original_message_id: str
    recipient: str
    subject: str
    body: str
    tone: str                # "formal", "casual", "friendly", "professional"
    confidence: float
    generated_at: datetime
    approved: bool = False
    edited: bool = False
    sent: bool = False
```

### SentimentAnalysis (`core/sentiment_analyzer.py`)
```python
@dataclass
class SentimentAnalysis:
    message_id: str
    tone: str                # "positive", "neutral", "negative", "urgent"
    urgency_score: float     # 0-10
    confidence: float
    keywords: list[str]
    analyzed_at: datetime
```

### Digest (`core/digest_generator.py`)
```python
@dataclass
class Digest:
    id: str
    period: str              # "daily", "weekly", "custom"
    start_time: datetime
    end_time: datetime
    summary: str
    message_count: int
    by_source: dict[str, int]    # {"gmail": 10, "slack": 25}
    by_sender: dict[str, int]    # Top senders
    action_items: list[str]
    urgent_count: int
    generated_at: datetime
```

### MultiStepCommand (`core/multi_agent_coordinator.py`)
```python
@dataclass
class SubTask:
    id: str
    action: str
    target: str
    parameters: dict[str, Any]
    depends_on: Optional[str] = None
    status: str = "pending"  # "pending", "executing", "completed", "failed"
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class MultiStepCommand:
    id: str
    original_command: str
    sub_tasks: list[SubTask]
    current_step: int = 0
    state: dict[str, Any]    # Shared state between tasks
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
```

### AgentConfig (`agents/base_agent.py`)
```python
class AgentConfig(BaseModel):
    name: str
    enabled: bool = True
    endpoint: str = ""
    timeout: int = 10
    retry_attempts: int = 3
```

### AgentResponse (`agents/base_agent.py`)
```python
class AgentResponse(BaseModel):
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime
    agent_name: str
```

## Exception Types

### Agent Exceptions (`agents/base_agent.py`)
```python
class AgentError(Exception):
    """Base exception for agent errors"""

class AuthenticationError(AgentError):
    """OAuth or token authentication failed"""

class RateLimitError(AgentError):
    """API rate limit exceeded"""

class NetworkError(AgentError):
    """Network connectivity issue"""
```

## Event Types

### Event Bus Events
```python
# Orchestrator Events
"intent.classified"              # Intent → Agents
"agent.{target}.{action}"        # Specific agent routing
"orchestrator.error"             # Error notification

# Agent Events
"agent.response"                 # Agent → Orchestrator/UI
"notification.new"               # Agent → Notification Hub

# UI Events
"ui.action"                      # UI → Orchestrator
"ui.update"                      # System → UI
"ui.notification"                # System → UI
"ui.error"                       # System → UI

# Voice Events
"voice.command"                  # Voice → Orchestrator
"voice.speak"                    # System → Voice
```

## Configuration Types

### Main Config (`config/config.yaml`)
```yaml
app:
  name: string
  version: string
  log_level: string

orchestrator:
  llm_model: string
  confidence_threshold: float
  context_window: int

voice:
  wake_word: string
  enabled: boolean

notifications:
  quiet_hours:
    enabled: boolean
    start: time
    end: time
```

### Agent Config (`config/agents.yaml`)
```yaml
agents:
  {agent_name}:
    enabled: boolean
    scopes: list[string]
    timeout: int
    retry_attempts: int
```

## Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    user_input TEXT,
    intent_json TEXT,
    agent_response TEXT,
    embedding BLOB,
    context_id TEXT
)
```

### Context Table
```sql
CREATE TABLE context (
    session_id TEXT PRIMARY KEY,
    last_active DATETIME,
    context_json TEXT
)
```

### Preferences Table
```sql
CREATE TABLE preferences (
    key TEXT PRIMARY KEY,
    value TEXT
)
```

## Function Signatures

### Core Functions

#### Orchestrator
```python
async def process_intent(user_input: str, context_id: str = "default") -> None
async def classify_intent(user_input: str, context: list[dict], context_id: str) -> Intent
async def route_to_agent(intent: Intent) -> None
async def handle_agent_response(response: dict[str, Any]) -> None
```

#### Event Bus
```python
async def emit(event: str, data: dict[str, Any]) -> None
async def subscribe(event: str, handler: Callable) -> None
async def unsubscribe(event: str, handler: Callable) -> None
async def start() -> None
async def stop() -> None
```

#### Local LLM
```python
async def generate(prompt: str, system: str = "", temperature: Optional[float] = None) -> str
async def classify_intent(prompt: str, context: list[dict]) -> dict[str, Any]
async def extract_task(message: str) -> Optional[dict[str, Any]]
```

#### Memory Store
```python
async def initialize() -> None
async def store_interaction(intent: Intent, response: str, embedding: Optional[np.ndarray] = None) -> None
async def get_recent_context(limit: int = 10, context_id: str = "default") -> list[dict]
async def search_similar(query_embedding: np.ndarray, k: int = 5) -> list[dict]
async def clear_session(session_id: str) -> None
async def prune_old_data(days: int = 30) -> None
async def get_preference(key: str) -> Optional[str]
async def set_preference(key: str, value: str) -> None
```

#### Notification Hub
```python
async def handle_notification(notification: Notification) -> None
async def deliver_queued_notifications() -> None
def get_notification_history(limit: int = 50) -> list[Notification]
```

#### Task Extractor
```python
async def extract_from_message(message_text: str, source: str, message_id: str, sender: str) -> Optional[Task]
def get_prioritized_tasks(limit: int = 10, include_completed: bool = False) -> list[Task]
def mark_task_completed(task_id: str) -> bool
```

#### Draft Manager
```python
async def generate_draft(original_message: dict, context: Optional[list[dict]] = None) -> EmailDraft
async def approve_draft(draft_id: str, edited_body: Optional[str] = None) -> bool
async def reject_draft(draft_id: str, reason: Optional[str] = None) -> bool
def get_pending_drafts(limit: int = 10) -> list[EmailDraft]
```

#### Learning Engine
```python
async def initialize() -> None
async def learn_from_interaction(sender: str, action: str, metadata: Optional[dict] = None) -> None
async def learn_from_edit(original: str, edited: str, tone: str) -> None
async def get_preferred_tone(sender: str) -> Optional[str]
def is_priority_sender(sender: str) -> bool
async def add_priority_sender(sender: str) -> None
```

#### Sentiment Analyzer
```python
async def analyze_message(message: dict, sender_priority: bool = False) -> SentimentAnalysis
def get_priority_from_sentiment(analysis: SentimentAnalysis) -> str
```

#### Digest Generator
```python
async def generate_digest(period: str = "daily", start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Digest
def format_digest_text(digest: Digest) -> str
```

#### Multi-Agent Coordinator
```python
async def execute_multi_step(command: str, context_id: str = "default") -> None
def get_active_commands() -> list[MultiStepCommand]
def get_command_history(limit: int = 10) -> list[MultiStepCommand]
```

### Agent Functions

#### Base Agent
```python
async def authenticate() -> bool
async def fetch(params: dict[str, Any]) -> list[dict[str, Any]]
async def act(action: str, data: dict[str, Any]) -> bool
async def handle_intent(action: str, params: dict[str, Any]) -> AgentResponse
```

## Type Aliases

```python
# Common type aliases used throughout the project
EventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
MessageDict = dict[str, Any]
ConfigDict = dict[str, Any]
```

## Import Paths

```python
# Core imports
from core.orchestrator import Orchestrator, Intent
from core.event_bus import EventBus
from core.llm import LocalLLM
from core.notification_hub import NotificationHub, Notification, Priority
from core.task_extractor import TaskExtractor, Task
from core.draft_manager import DraftManager, EmailDraft
from core.learning_engine import LearningEngine
from core.sentiment_analyzer import SentimentAnalyzer, SentimentAnalysis
from core.digest_generator import DigestGenerator, Digest
from core.multi_agent_coordinator import MultiAgentCoordinator, MultiStepCommand

# Database imports
from database.memory import MemoryStore

# Agent imports
from agents.base_agent import BaseAgent, AgentConfig, AgentResponse
from agents.base_agent import AgentError, AuthenticationError, RateLimitError, NetworkError
```

---

*This index is auto-generated from the AUTOCOM codebase. Last updated: 2025-11-11*
