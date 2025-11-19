# AUTOCOM Function Index

> Complete reference of all functions, methods, and their locations

## Core Module Functions

### `core/orchestrator.py`

#### `Orchestrator` class
- `__init__(llm, memory, event_bus, confidence_threshold=0.7)` - Initialize orchestrator
- `async register_agent(name: str, agent: Any)` - Register agent with orchestrator
- `async process_intent(user_input: str, context_id: str = "default")` - Main entry point for intent processing
- `async classify_intent(user_input: str, context: list[dict], context_id: str) -> Intent` - Classify user input into structured intent
- `async route_to_agent(intent: Intent)` - Route intent to appropriate agent
- `async handle_agent_response(response: dict[str, Any])` - Handle responses from agents
- `async _request_clarification(user_input: str)` - Request clarification for ambiguous intents

### `core/event_bus.py`

#### `EventBus` class
- `__init__(max_queue_size: int = 1000)` - Initialize event bus
- `async emit(event: str, data: dict[str, Any])` - Publish event to bus
- `async subscribe(event: str, handler: Callable)` - Subscribe handler to event
- `async unsubscribe(event: str, handler: Callable)` - Unsubscribe handler from event
- `async start()` - Start event processing loop
- `async stop()` - Stop event bus gracefully
- `async _process_events()` - Internal event processing loop
- `async _safe_handler_call(handler: Callable, data: dict)` - Call handler with error isolation
- `get_stats() -> dict[str, Any]` - Get event bus statistics

### `core/llm.py`

#### `LocalLLM` class
- `__init__(model="llama3.1:8b", endpoint="http://localhost:11434", temperature=0.3, max_tokens=500)` - Initialize LLM client
- `async generate(prompt: str, system: str = "", temperature: Optional[float] = None) -> str` - Generate text completion
- `async classify_intent(prompt: str, context: list[dict]) -> dict[str, Any]` - Classify intent into structured format
- `async extract_task(message: str) -> Optional[dict[str, Any]]` - Extract actionable task from message
- `_fallback_parse(prompt: str) -> dict[str, Any]` - Rule-based fallback parsing
- `async close()` - Close HTTP client

### `core/notification_hub.py`

#### `NotificationHub` class
- `__init__(event_bus, quiet_hours_start, quiet_hours_end, urgent_override=True)` - Initialize notification hub
- `async handle_notification(notification: Notification)` - Process incoming notification
- `_should_suppress(notification: Notification) -> bool` - Check if notification should be suppressed
- `_is_quiet_hours() -> bool` - Check if current time is in quiet hours
- `async _queue_for_later(notification: Notification)` - Queue notification for later delivery
- `async _deliver(notification: Notification)` - Deliver notification through channels
- `async deliver_queued_notifications()` - Deliver all queued notifications
- `_create_queued_summary() -> Notification` - Create summary of queued notifications
- `async get_notification_history(limit: int = 50) -> list[Notification]` - Get recent notifications
- `get_stats() -> dict[str, Any]` - Get notification hub statistics

### `core/task_extractor.py`

#### `TaskExtractor` class
- `__init__(llm: Any)` - Initialize task extractor
- `async extract_from_message(message_text: str, source: str, message_id: str, sender: str) -> Optional[Task]` - Extract task from message
- `_contains_task_indicators(text: str) -> bool` - Check for task indicator keywords
- `_calculate_priority(text: str, llm_priority: str) -> str` - Calculate task priority
- `_rule_based_extraction(text: str, source: str, message_id: str, sender: str) -> Optional[Task]` - Fallback rule-based extraction
- `get_prioritized_tasks(limit: int = 10, include_completed: bool = False) -> list[Task]` - Get tasks sorted by priority
- `mark_task_completed(task_id: str) -> bool` - Mark task as completed
- `get_task_stats() -> dict[str, Any]` - Get task extraction statistics

### `core/draft_manager.py`

#### `DraftManager` class
- `__init__(llm: Any, learning_engine: Any)` - Initialize draft manager
- `async generate_draft(original_message: dict, context: Optional[list[dict]] = None) -> EmailDraft` - Generate draft reply
- `_is_important_sender(sender: str) -> bool` - Determine if sender is important
- `_build_draft_prompt(original_message: dict, tone: str, context: Optional[list[dict]]) -> str` - Build LLM prompt
- `async approve_draft(draft_id: str, edited_body: Optional[str] = None) -> bool` - Approve draft for sending
- `async reject_draft(draft_id: str, reason: Optional[str] = None) -> bool` - Reject draft
- `get_pending_drafts(limit: int = 10) -> list[EmailDraft]` - Get pending drafts
- `mark_draft_sent(draft_id: str) -> bool` - Mark draft as sent
- `get_draft_stats() -> dict[str, Any]` - Get draft generation statistics

### `core/learning_engine.py`

#### `LearningEngine` class
- `__init__(memory_store: Any)` - Initialize learning engine
- `async initialize()` - Load learned preferences from storage
- `async save_preferences()` - Persist learned preferences
- `async learn_from_interaction(sender: str, action: str, metadata: Optional[dict] = None)` - Learn from user interaction
- `async learn_from_edit(original: str, edited: str, tone: str)` - Learn from draft edits
- `async learn_from_rejection(tone: str, reason: Optional[str])` - Learn from draft rejections
- `async get_preferred_tone(sender: str) -> Optional[str]` - Get preferred tone for sender
- `is_priority_sender(sender: str) -> bool` - Check if sender is priority
- `is_ignored_sender(sender: str) -> bool` - Check if sender should be ignored
- `async add_priority_sender(sender: str)` - Manually add priority sender
- `async remove_priority_sender(sender: str)` - Remove priority sender
- `get_sender_stats(sender: str) -> Optional[dict]` - Get interaction statistics for sender
- `get_top_senders(limit: int = 10) -> list[tuple[str, int]]` - Get most frequently interacted senders
- `get_learning_stats() -> dict[str, Any]` - Get learning engine statistics

### `core/sentiment_analyzer.py`

#### `SentimentAnalyzer` class
- `__init__(llm: Any)` - Initialize sentiment analyzer
- `async analyze_message(message: dict, sender_priority: bool = False) -> SentimentAnalysis` - Analyze message sentiment
- `_calculate_urgency_score(text: str, sender_priority: bool) -> float` - Calculate urgency score
- `_detect_tone(text: str, urgency_score: float) -> str` - Detect emotional tone
- `_extract_keywords(text: str) -> list[str]` - Extract important keywords
- `get_priority_from_sentiment(analysis: SentimentAnalysis) -> str` - Convert sentiment to priority
- `clear_cache()` - Clear analysis cache
- `get_stats() -> dict[str, Any]` - Get sentiment analyzer statistics

### `core/digest_generator.py`

#### `DigestGenerator` class
- `__init__(llm: Any, memory_store: Any, task_extractor: Any)` - Initialize digest generator
- `async generate_digest(period: str = "daily", start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Digest` - Generate communication digest
- `async _fetch_messages(start_time: datetime, end_time: datetime) -> list[dict]` - Fetch messages from memory
- `_categorize_messages(messages: list[dict]) -> tuple[dict, dict]` - Categorize by source and sender
- `async _extract_action_items(messages: list[dict]) -> list[str]` - Extract action items
- `async _generate_summary(messages: list[dict], period: str) -> str` - Generate natural language summary
- `_create_empty_digest(period: str, start_time: datetime, end_time: datetime) -> Digest` - Create empty digest
- `format_digest_text(digest: Digest) -> str` - Format digest as readable text
- `get_recent_digests(limit: int = 5) -> list[Digest]` - Get recently generated digests
- `get_stats() -> dict[str, Any]` - Get digest generator statistics

### `core/multi_agent_coordinator.py`

#### `MultiAgentCoordinator` class
- `__init__(orchestrator: Any, event_bus: EventBus, llm: Any)` - Initialize coordinator
- `async execute_multi_step(command: str, context_id: str = "default")` - Execute multi-step command
- `async _decompose_command(command: str) -> list[SubTask]` - Decompose command into sub-tasks
- `async _execute_sub_task(command_id: str, sub_task: SubTask) -> dict[str, Any]` - Execute single sub-task
- `async _handle_failure(command_id: str, error: str)` - Handle sub-task failure
- `async _report_success(command: MultiStepCommand)` - Report successful completion
- `get_active_commands() -> list[MultiStepCommand]` - Get currently executing commands
- `get_command_history(limit: int = 10) -> list[MultiStepCommand]` - Get command execution history
- `get_stats() -> dict[str, Any]` - Get coordinator statistics

### `core/main.py`

#### `AutocomApp` class
- `__init__()` - Initialize application
- `async initialize()` - Initialize all components
- `_load_config() -> dict` - Load configuration from YAML
- `async run()` - Run main application loop
- `async shutdown()` - Gracefully shutdown all components
- `setup_signal_handlers()` - Setup signal handlers for shutdown

#### Module-level functions
- `async main()` - Main entry point

## Database Module Functions

### `database/memory.py`

#### `MemoryStore` class
- `__init__(db_path: str = "memory/context.db")` - Initialize memory store
- `async initialize()` - Create database tables
- `async _create_tables()` - Create database schema
- `async store_interaction(intent: Intent, response: str, embedding: Optional[np.ndarray] = None)` - Store user interaction
- `async get_recent_context(limit: int = 10, context_id: str = "default") -> list[dict]` - Retrieve recent conversation history
- `async search_similar(query_embedding: np.ndarray, k: int = 5) -> list[dict]` - Search for similar interactions
- `async clear_session(session_id: str)` - Clear conversation history for session
- `async prune_old_data(days: int = 30)` - Remove old conversation history
- `async get_preference(key: str) -> Optional[str]` - Get preference value
- `async set_preference(key: str, value: str)` - Set preference value
- `async close()` - Close database connection
- `@staticmethod _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float` - Calculate cosine similarity

## Agent Module Functions

### `agents/base_agent.py`

#### `BaseAgent` class (Abstract)
- `__init__(config: AgentConfig)` - Initialize agent
- `@abstractmethod async authenticate() -> bool` - Perform authentication
- `@abstractmethod async fetch(params: dict[str, Any]) -> list[dict[str, Any]]` - Retrieve data from service
- `@abstractmethod async act(action: str, data: dict[str, Any]) -> bool` - Execute action on service
- `async handle_intent(action: str, params: dict[str, Any]) -> AgentResponse` - Main entry point for intent handling
- `async _retry_request(func: Any, *args, **kwargs) -> Any` - Wrapper for retrying requests
- `__repr__() -> str` - String representation

## Utility Functions

### Common Patterns

#### Async Context Managers
```python
async with component:
    # Component lifecycle management
    pass
```

#### Retry Decorator
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def network_call():
    pass
```

#### Event Handler Pattern
```python
async def handle_event(data: dict[str, Any]) -> None:
    # Process event
    pass

await event_bus.subscribe("event_name", handle_event)
```

## Function Call Flows

### Voice Command Flow
```
1. voice.wake.detect_wake_word()
2. voice.stt.transcribe_audio()
3. orchestrator.process_intent()
4. orchestrator.classify_intent()
5. orchestrator.route_to_agent()
6. agent.handle_intent()
7. agent.fetch() or agent.act()
8. orchestrator.handle_agent_response()
9. event_bus.emit("ui.update")
10. voice.tts.speak()
```

### Message Processing Flow
```
1. agent.fetch() [Gmail/Slack]
2. event_bus.emit("notification.new")
3. notification_hub.handle_notification()
4. sentiment_analyzer.analyze_message()
5. task_extractor.extract_from_message()
6. draft_manager.generate_draft()
7. learning_engine.learn_from_interaction()
8. notification_hub._deliver()
```

### Multi-Step Command Flow
```
1. orchestrator.process_intent()
2. multi_agent_coordinator.execute_multi_step()
3. multi_agent_coordinator._decompose_command()
4. For each sub_task:
   a. multi_agent_coordinator._execute_sub_task()
   b. orchestrator.route_to_agent()
   c. agent.handle_intent()
5. multi_agent_coordinator._report_success()
```

---

*This index is auto-generated from the AUTOCOM codebase. Last updated: 2025-11-11*
