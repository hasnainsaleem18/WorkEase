# Design Document - AutoReturn Rebuild

## Overview

AutoReturn is a voice-first, AI-powered communication automation platform that provides a unified interface for Gmail and Slack. **The local Ollama LLM serves as the central brain and decision-maker**, understanding user intent, analyzing messages, generating responses, and making intelligent routing decisions. The system architecture is built on event-driven principles with asynchronous communication between loosely coupled components. All AI processing occurs locally to ensure complete privacy.

### Key Design Principles

1. **LLM-Centric Architecture**: Local Ollama LLM is the central intelligence that makes all decisions
2. **Privacy-First**: All AI inference happens locally on-device, zero external API calls
3. **Event-Driven Architecture**: Components communicate via asynchronous event bus for loose coupling
4. **Async-First**: All I/O operations use async/await for non-blocking execution
5. **Modular Design**: Each component is independent and replaceable
6. **Algorithm-Centric**: Custom implementations demonstrate algorithmic expertise

### LLM as the Brain

The local Ollama LLM (Llama 3.1) is the **core decision-making engine** that:
- **Understands** natural language commands and user intent
- **Analyzes** incoming messages for sentiment, urgency, and action items
- **Decides** which actions to take and which agents to invoke
- **Generates** draft replies with appropriate tone and content
- **Learns** from user interactions to improve over time
- **Reasons** about context and conversation history

All other components (orchestrator, agents, algorithms) execute the LLM's decisions and provide supporting functionality.

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Desktop UI  │  │ System Tray │  │ Voice Interface     │  │
│  │ (PyQt6)     │  │             │  │ (Wake/STT/TTS)      │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼─────────────────────┼─────────────┘
          │                │                     │
          └────────────────┼─────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 AI DECISION LAYER (BRAIN)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           LOCAL LLM (Ollama - Llama 3.1)            │    │
│  │  • Intent Understanding & Classification             │    │
│  │  • Decision Making & Command Routing                 │    │
│  │  • Natural Language Processing                       │    │
│  │  • Draft Generation & Content Creation               │    │
│  │  • Context Understanding & Memory                    │    │
│  └──────────────────────┬──────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   ORCHESTRATOR                       │    │
│  │  (Executes LLM Decisions, Coordinates Actions)       │    │
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
│  ┌─────────────┐  ┌─────────────┐                           │
│  │ Gmail Agent │  │ Slack Agent │                           │
│  └──────┬──────┘  └──────┬──────┘                           │
└─────────┼────────────────┼─────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLite Database (Local)                 │    │
│  │  - Messages, Tasks, Preferences, Context, Logs       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Voice Command Flow:
User speaks → Wake Word Detector → STT → 
Local LLM (Understands Intent & Makes Decision) → 
Orchestrator (Executes LLM Decision) → Event Bus → 
Agent (Gmail/Slack) → Action Performed → 
Event Bus → TTS → User hears response

Message Arrival Flow:
Gmail/Slack API → Agent → Event Bus → 
Local LLM (Analyzes Content & Determines Priority) →
[Task Extractor, Sentiment Analyzer, Priority Scorer] → 
Notification Hub → UI Update + Pop-up

Draft Generation Flow:
User requests reply → Orchestrator → 
Local LLM (Reads Original Message & Generates Draft) →
Draft Manager (Ranks & Presents Options) → 
User selects/edits → Learning Engine (Learns Preferences)
```


## Components and Interfaces

### 1. Local LLM (Ollama) - The Brain

**Role**: Central intelligence and decision-making engine for the entire application

**Responsibilities**:
- **Intent Classification**: Understand what the user wants to do from natural language
- **Decision Making**: Determine which actions to take and which agents to invoke
- **Content Analysis**: Analyze messages for sentiment, urgency, priority, and action items
- **Draft Generation**: Create appropriate email/message replies with correct tone
- **Context Understanding**: Maintain conversation history and resolve references
- **Learning**: Adapt to user preferences and improve responses over time

**Technology**: Ollama with Llama 3.1 8B (or smaller models for resource-constrained systems)

**Interface**:
```python
class LocalLLM:
    """Central AI brain of AutoReturn"""
    
    async def understand_intent(self, user_input: str, context: List[Context]) -> Intent:
        """
        Analyze user command and determine intent.
        Returns: Intent with action, target, parameters, and confidence
        """
        pass
    
    async def analyze_message(self, message: Message) -> MessageAnalysis:
        """
        Analyze incoming message for sentiment, urgency, priority.
        Returns: Analysis with sentiment score, urgency level, extracted tasks
        """
        pass
    
    async def generate_draft(self, original_message: Message, context: str) -> str:
        """
        Generate appropriate reply draft.
        Returns: Draft text with appropriate tone and content
        """
        pass
    
    async def extract_tasks(self, text: str) -> List[Task]:
        """
        Identify action items in text.
        Returns: List of tasks with priorities and deadlines
        """
        pass
    
    async def make_decision(self, situation: dict) -> Decision:
        """
        Make intelligent decision based on current situation.
        Returns: Decision with recommended actions
        """
        pass
    
    async def learn_from_feedback(self, original: str, edited: str, feedback: str) -> None:
        """
        Learn from user corrections and feedback.
        Updates internal preferences and patterns
        """
        pass
```

**Prompt Engineering**:
The LLM uses carefully crafted prompts for each task:

1. **Intent Classification Prompt**:
```
You are the brain of AutoReturn, a communication automation assistant.
Analyze this user command and determine:
- Action: what they want to do (send, fetch, create, delete, update)
- Target: which service (gmail, slack)
- Parameters: recipients, subject, content, etc.
- Confidence: how certain you are (0.0 to 1.0)

User command: "{user_input}"
Recent context: {context}

Respond in JSON format: {{"action": "...", "target": "...", "parameters": {{...}}, "confidence": 0.95}}
```

2. **Message Analysis Prompt**:
```
Analyze this message and provide:
- Sentiment: positive/negative/neutral (-1.0 to 1.0)
- Urgency: how urgent (0-10 scale)
- Priority: overall priority (0-100)
- Tasks: any action items found
- Tone: URGENT/NEGATIVE/POSITIVE/NEUTRAL

Message: "{message_content}"
Sender: {sender}
Subject: {subject}

Respond in JSON format.
```

3. **Draft Generation Prompt**:
```
Generate an appropriate reply to this message.
Match the tone of the original sender.
Address all key points mentioned.
Keep it concise and professional.

Original message: "{original_message}"
Sender: {sender}
Context: {context}

Generate reply:
```

**Privacy Guarantee**: All LLM processing happens locally via Ollama. No data is ever sent to external APIs.

---

### 2. Orchestrator

**Role**: Executes decisions made by the LLM and coordinates component actions

**Responsibilities**:
- Receive commands from UI and voice interface
- Send commands to LLM for understanding
- Execute LLM decisions by invoking appropriate components
- Route events through the event bus
- Manage conversation context

**Interface**:
```python
class Orchestrator:
    def __init__(self, llm: LocalLLM, event_bus: EventBus, db: DatabaseManager):
        self.llm = llm  # The brain
        self.event_bus = event_bus
        self.db = db
    
    async def process_command(self, text: str) -> None:
        """
        Process user command by consulting LLM and executing decision.
        """
        # 1. Get context from database
        context = await self.db.get_recent_context()
        
        # 2. Ask LLM to understand intent
        intent = await self.llm.understand_intent(text, context)
        
        # 3. Execute LLM's decision
        await self.execute_intent(intent)
    
    async def execute_intent(self, intent: Intent) -> None:
        """Execute the LLM's decision by routing to appropriate handler."""
        pass
    
    async def handle_new_message(self, message: Message) -> None:
        """
        Handle incoming message by asking LLM to analyze it.
        """
        # 1. Ask LLM to analyze message
        analysis = await self.llm.analyze_message(message)
        
        # 2. Execute based on LLM's analysis
        await self.process_analysis(message, analysis)
```

**Key Point**: The orchestrator doesn't make decisions—it executes what the LLM decides.

---

### 3. Voice Pipeline

#### Wake Word Detector
- **Purpose**: Detect "Hey Auto" activation phrase
- **Technology**: Porcupine wake word engine
- **Interface**:
  ```python
  class WakeWordDetector:
      async def start_listening(self) -> None
      async def stop_listening(self) -> None
      def on_wake_word_detected(self, callback: Callable) -> None
  ```

#### Speech-to-Text (STT)
- **Purpose**: Convert audio to text for LLM processing
- **Technology**: Whisper.cpp for local processing
- **Interface**:
  ```python
  class SpeechToText:
      async def transcribe(self, audio: bytes) -> str
      def set_language(self, lang: str) -> None
  ```

#### Text-to-Speech (TTS)
- **Purpose**: Convert LLM responses to audio
- **Technology**: Piper TTS
- **Interface**:
  ```python
  class TextToSpeech:
      async def speak(self, text: str) -> None
      def set_voice(self, voice_id: str) -> None
  ```

---

### 4. Event Bus

- **Purpose**: Asynchronous pub/sub messaging between components
- **Responsibilities**:
  - Decouple components
  - Handle backpressure
  - Isolate failures
- **Interface**:
  ```python
  class EventBus:
      async def emit(self, event: str, data: dict) -> None
      async def subscribe(self, event: str, handler: Callable) -> None
      async def unsubscribe(self, event: str, handler: Callable) -> None
      async def start(self) -> None
  ```

---

### 5. Gmail Agent

- **Purpose**: Execute Gmail operations as directed by LLM
- **Responsibilities**:
  - OAuth2 authentication
  - Fetch/send emails
  - Mark read, archive, delete
- **Interface**:
  ```python
  class GmailAgent:
      async def authenticate(self) -> bool
      async def fetch_messages(self, params: dict) -> List[Message]
      async def send_message(self, to: str, subject: str, body: str) -> bool
      async def mark_read(self, message_id: str) -> bool
      async def archive(self, message_id: str) -> bool
  ```

**Key Point**: Gmail agent doesn't decide what to do—it executes LLM's decisions.

---

### 6. Slack Agent

- **Purpose**: Execute Slack operations as directed by LLM
- **Responsibilities**:
  - OAuth2 authentication
  - Fetch/send messages
  - Real-time monitoring
  - Status management
- **Interface**:
  ```python
  class SlackAgent:
      async def authenticate(self) -> bool
      async def fetch_messages(self, params: dict) -> List[Message]
      async def send_message(self, channel: str, text: str) -> bool
      async def start_realtime(self) -> None
      async def set_status(self, status: str) -> bool
  ```

**Key Point**: Slack agent doesn't decide what to do—it executes LLM's decisions.

---

### 7. Supporting Algorithms

These algorithms support the LLM's decision-making:

#### Priority Scorer
- Calculates message priority scores
- Used by LLM for priority analysis
- **Interface**: `calculate_priority(message: Message) -> float`

#### Sentiment Analyzer
- Analyzes text sentiment and urgency
- Provides input to LLM
- **Interface**: `analyze(text: str) -> SentimentResult`

#### Task Extractor
- Extracts action items from text
- Works alongside LLM
- **Interface**: `extract_tasks(message: Message) -> List[Task]`

#### Learning Engine
- Tracks user interactions
- Helps LLM adapt to preferences
- **Interface**: `track_interaction(sender: str, action: str) -> None`

#### Context Matcher
- Finds relevant past conversations
- Provides context to LLM
- **Interface**: `find_context(query: str) -> List[Context]`

---

### 8. Notification Hub

- **Purpose**: Manage notifications based on LLM's priority analysis
- **Algorithm**: Priority-based queuing + quiet hours + batching
- **Interface**:
  ```python
  class NotificationHub:
      async def notify(self, notification: Notification) -> None
      def is_quiet_hours(self) -> bool
      def should_batch(self, notifications: List[Notification]) -> bool
  ```

---

### 9. Database Manager

- **Purpose**: Local data persistence
- **Technology**: SQLite with encryption
- **Schema**:
  ```sql
  messages (id, source, sender, subject, content, timestamp, priority, read)
  tasks (id, title, description, priority, source_message_id, deadline, completed)
  preferences (key, value)
  context (id, command, response, timestamp)
  sender_weights (sender, weight, interactions, last_interaction)
  llm_interactions (id, prompt, response, feedback, timestamp)
  audit_log (id, action, details, timestamp)
  ```

---

### 10. Desktop UI (PyQt6)

- **Purpose**: Native desktop interface
- **Components**:
  - Main Window: Dashboard with inbox, tasks, drafts
  - Message List: Displays messages with LLM-calculated priorities
  - Message Detail: Shows full content with LLM-generated insights
  - Settings Panel: Configuration interface
  - System Tray: Background operation
  - Notification Popup: Quick action dialogs

