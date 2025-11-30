# 🏗️ System Architecture Document

## 1. Architecture Overview

### 1.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Desktop UI  │  │ System Tray │  │ Voice Interface     │  │
│  │ (PyQt6)     │  │             │  │ (Wake/STT/TTS)      │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼─────────────────────┼─────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   ORCHESTRATOR                       │    │
│  │  (Intent Classification, Command Routing)            │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │                    EVENT BUS                         │    │
│  │  (Async Pub/Sub Communication)                       │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│  ┌──────────┬───────────┼───────────┬──────────────────┐    │
│  ▼          ▼           ▼           ▼                  ▼    │
│ ┌────┐   ┌────┐    ┌────────┐   ┌────────┐    ┌──────────┐ │
│ │Task│   │Draft│   │Notif.  │   │Learning│    │Sentiment │ │
│ │Ext.│   │Mgr. │   │Hub     │   │Engine  │    │Analyzer  │ │
│ └────┘   └────┘    └────────┘   └────────┘    └──────────┘ │
└─────────────────────────────────────────────────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Gmail Agent │  │ Slack Agent │  │ Local LLM (Ollama)  │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼─────────────────────┼─────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLite Database (Local)                 │    │
│  │  - Messages, Tasks, Preferences, Context, Logs       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  ┌─────────────┐  ┌─────────────┐                           │
│  │ Gmail API   │  │ Slack API   │                           │
│  └─────────────┘  └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Details

### 2.1 Presentation Layer

#### Desktop UI (PyQt6)
- Main dashboard window
- Message list and detail views
- Settings panel
- Task list view

#### System Tray
- Background operation
- Quick access menu
- Unread count badge

#### Voice Interface
- Wake word detection (Porcupine)
- Speech-to-text (Whisper)
- Text-to-speech (Piper)

---

### 2.2 Application Layer

#### Orchestrator
**Purpose:** Central command processor  
**Responsibilities:**
- Receive user commands (voice/UI)
- Classify intent using LLM
- Route to appropriate handler
- Manage conversation context

#### Event Bus
**Purpose:** Inter-component communication  
**Responsibilities:**
- Async pub/sub messaging
- Decouple components
- Handle backpressure
- Error isolation

#### Task Extractor
**Purpose:** Find action items in messages  
**Responsibilities:**
- Analyze message text
- Detect action verbs
- Extract deadlines
- Assign priorities

#### Draft Manager
**Purpose:** Generate email replies  
**Responsibilities:**
- Analyze original message
- Generate appropriate reply
- Match tone to sender
- Learn from edits

#### Notification Hub
**Purpose:** Manage all notifications  
**Responsibilities:**
- Priority-based queuing
- Quiet hours filtering
- Multi-channel delivery
- Batching similar notifications

#### Learning Engine
**Purpose:** Adapt to user preferences  
**Responsibilities:**
- Track interactions
- Detect patterns
- Update weights
- Improve over time

#### Sentiment Analyzer
**Purpose:** Detect urgency and tone  
**Responsibilities:**
- Analyze message sentiment
- Calculate urgency score
- Classify tone
- Feed into priority scoring

---

### 2.3 Integration Layer

#### Gmail Agent
**Purpose:** Gmail API integration  
**Responsibilities:**
- OAuth2 authentication
- Fetch emails
- Send emails
- Mark read, archive

#### Slack Agent
**Purpose:** Slack API integration  
**Responsibilities:**
- OAuth2 authentication
- Fetch messages
- Send messages
- Real-time monitoring (WebSocket)

#### Local LLM
**Purpose:** AI processing  
**Responsibilities:**
- Intent classification
- Text generation
- Summarization
- All processing local (privacy)

---

### 2.4 Data Layer

#### SQLite Database
**Tables:**
- `messages` - Cached messages
- `tasks` - Extracted tasks
- `preferences` - User settings
- `context` - Conversation history
- `audit_log` - Action history

---

## 3. Data Flow

### 3.1 Voice Command Flow
```
User speaks "Check my emails"
         │
         ▼
┌─────────────────┐
│ Wake Word       │ ← Detects "Hey Auto"
│ Detection       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Speech-to-Text  │ ← Transcribes audio
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Orchestrator    │ ← Classifies intent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Event Bus       │ ← Routes to Gmail Agent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gmail Agent     │ ← Fetches emails
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Event Bus       │ ← Returns results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text-to-Speech  │ ← Speaks response
└─────────────────┘
```

### 3.2 Notification Flow
```
New email arrives (Gmail API)
         │
         ▼
┌─────────────────┐
│ Gmail Agent     │ ← Receives email
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Event Bus       │ ← Emits "new_message" event
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌───────┐ ┌──────────┐
│Task   │ │Sent.  │ │Notif.    │
│Extract│ │Analyz.│ │Hub       │
└───┬───┘ └───┬───┘ └────┬─────┘
    │         │          │
    │         └────┬─────┘
    │              ▼
    │      ┌──────────────┐
    │      │ Priority     │ ← Calculates priority
    │      │ Scoring      │
    │      └──────┬───────┘
    │             │
    │             ▼
    │      ┌──────────────┐
    │      │ Show         │ ← Displays notification
    │      │ Notification │
    │      └──────────────┘
    │
    ▼
┌─────────────────┐
│ Task List       │ ← Adds extracted task
└─────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| UI | PyQt6 | Desktop interface |
| Voice | Porcupine | Wake word |
| Voice | Whisper.cpp | Speech-to-text |
| Voice | Piper | Text-to-speech |
| Backend | Python 3.10+ | Core logic |
| Async | asyncio | Non-blocking I/O |
| LLM | Ollama | Local AI |
| Database | SQLite | Local storage |
| Gmail | google-auth, gmail API | Email integration |
| Slack | slack-sdk | Chat integration |

---

## 5. Design Principles

### 5.1 Event-Driven Architecture
- Components communicate via events
- Loose coupling
- Easy to extend
- Fault isolation

### 5.2 Async-First
- All I/O operations are async
- Non-blocking
- Better performance
- Responsive UI

### 5.3 Privacy-First
- All AI processing local
- No cloud dependencies
- Encrypted storage
- User controls data

### 5.4 Modular Design
- Each component independent
- Easy to test
- Easy to replace
- Easy to extend

---

## 6. Scalability Considerations

| Aspect | Approach |
|--------|----------|
| Message Volume | Pagination, caching |
| Memory | LRU cache, pruning |
| CPU | Async processing |
| Storage | Auto-cleanup old data |
