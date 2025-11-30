# 🚀 Implementation Guide

## 1. Implementation Phases

### Phase 1: Project Setup (Week 1)
- [ ] Create project structure
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure linting/formatting
- [ ] Set up Git repository

### Phase 2: Core Backend (Weeks 2-3)
- [ ] Implement Event Bus
- [ ] Implement Orchestrator
- [ ] Implement LLM integration
- [ ] Implement Database layer
- [ ] Write unit tests

### Phase 3: Agents (Weeks 4-5)
- [ ] Implement Gmail Agent
- [ ] Implement Slack Agent
- [ ] Test OAuth flows
- [ ] Write integration tests

### Phase 4: Automation (Week 6)
- [ ] Implement Task Extractor
- [ ] Implement Sentiment Analyzer
- [ ] Implement Notification Hub
- [ ] Implement Learning Engine

### Phase 5: Voice (Weeks 7-8)
- [ ] Implement Wake Word Detection
- [ ] Implement Speech-to-Text
- [ ] Implement Text-to-Speech
- [ ] Integrate with Orchestrator

### Phase 6: UI (Weeks 9-10)
- [ ] Implement Main Window
- [ ] Implement Message List
- [ ] Implement Settings Panel
- [ ] Implement System Tray
- [ ] Implement Notifications

### Phase 7: Integration & Testing (Weeks 11-12)
- [ ] Wire all components
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Bug fixes

---

## 2. Step-by-Step Implementation

### Step 1: Project Setup
```bash
# Create project directory
mkdir autocom && cd autocom

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p core agents voice ui database algorithms config data
```

### Step 2: Event Bus
```python
# core/event_bus.py
import asyncio
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.queue = asyncio.Queue()
        self.running = False
    
    async def emit(self, event: str, data: dict) -> None:
        await self.queue.put((event, data))
    
    async def subscribe(self, event: str, handler: Callable) -> None:
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)
    
    async def start(self) -> None:
        self.running = True
        while self.running:
            event, data = await self.queue.get()
            handlers = self.subscribers.get(event, [])
            for handler in handlers:
                try:
                    await handler(data)
                except Exception as e:
                    print(f"Handler error: {e}")
    
    async def stop(self) -> None:
        self.running = False
```

### Step 3: LLM Integration
```python
# core/llm.py
import httpx

class LocalLLM:
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model
        self.endpoint = "http://localhost:11434"
    
    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            )
            return response.json()["response"]
    
    async def classify_intent(self, text: str) -> dict:
        prompt = f"""Classify this command:
        "{text}"
        
        Return JSON: {{"action": "...", "target": "...", "confidence": 0.0-1.0}}
        """
        response = await self.generate(prompt)
        # Parse JSON from response
        return self._parse_json(response)
```

### Step 4: Gmail Agent
```python
# agents/gmail_agent.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailAgent:
    def __init__(self):
        self.service = None
    
    async def authenticate(self) -> bool:
        # Load credentials from file
        creds = Credentials.from_authorized_user_file('config/gmail_token.json')
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    async def fetch(self, max_results: int = 10) -> list:
        results = self.service.users().messages().list(
            userId='me', maxResults=max_results, q='is:unread'
        ).execute()
        
        messages = []
        for msg in results.get('messages', []):
            full_msg = self.service.users().messages().get(
                userId='me', id=msg['id']
            ).execute()
            messages.append(self._parse_message(full_msg))
        
        return messages
    
    async def send(self, to: str, subject: str, body: str) -> bool:
        # Create and send email
        pass
```

### Step 5: Orchestrator
```python
# core/orchestrator.py
class Orchestrator:
    def __init__(self, llm, event_bus, agents):
        self.llm = llm
        self.event_bus = event_bus
        self.agents = agents
    
    async def process(self, text: str) -> None:
        # 1. Classify intent
        intent = await self.llm.classify_intent(text)
        
        # 2. Get appropriate agent
        agent = self.agents.get(intent['target'])
        if not agent:
            await self.event_bus.emit('error', {'message': 'Unknown target'})
            return
        
        # 3. Execute action
        if intent['action'] == 'fetch':
            results = await agent.fetch()
            await self.event_bus.emit('results', {'data': results})
        elif intent['action'] == 'send':
            success = await agent.send(intent['params'])
            await self.event_bus.emit('sent', {'success': success})
```

### Step 6: Main Application
```python
# core/main.py
import asyncio
from core.event_bus import EventBus
from core.orchestrator import Orchestrator
from core.llm import LocalLLM
from agents.gmail_agent import GmailAgent
from agents.slack_agent import SlackAgent

async def main():
    # Initialize components
    event_bus = EventBus()
    llm = LocalLLM()
    
    # Initialize agents
    gmail = GmailAgent()
    slack = SlackAgent()
    await gmail.authenticate()
    await slack.authenticate()
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        llm=llm,
        event_bus=event_bus,
        agents={'gmail': gmail, 'slack': slack}
    )
    
    # Start event bus
    asyncio.create_task(event_bus.start())
    
    # Main loop
    while True:
        command = input("Enter command: ")
        await orchestrator.process(command)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. Testing Strategy

### Unit Tests
```python
# tests/test_event_bus.py
import pytest
from core.event_bus import EventBus

@pytest.mark.asyncio
async def test_emit_and_subscribe():
    bus = EventBus()
    received = []
    
    async def handler(data):
        received.append(data)
    
    await bus.subscribe('test', handler)
    await bus.emit('test', {'value': 1})
    
    # Process event
    await asyncio.sleep(0.1)
    
    assert len(received) == 1
    assert received[0]['value'] == 1
```

### Integration Tests
```python
# tests/test_gmail_agent.py
@pytest.mark.asyncio
async def test_gmail_fetch():
    agent = GmailAgent()
    await agent.authenticate()
    
    messages = await agent.fetch(max_results=5)
    
    assert isinstance(messages, list)
    assert len(messages) <= 5
```

---

## 4. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Ollama not running | Start with `ollama serve` |
| OAuth token expired | Re-authenticate |
| Voice not working | Check microphone permissions |
| UI not responding | Check async/await usage |

---

## 5. Development Commands

```bash
# Run application
python -m core.main

# Run tests
pytest tests/ -v

# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```
