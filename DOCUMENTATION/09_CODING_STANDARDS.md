# 📝 Coding Standards

## 1. Python Style Guide

### 1.1 General Rules
- Follow PEP 8
- Use Python 3.10+ features
- Maximum line length: 88 characters
- Use type hints everywhere

### 1.2 Naming Conventions
```python
# Classes: PascalCase
class MessageHandler:
    pass

# Functions/methods: snake_case
def process_message():
    pass

# Variables: snake_case
message_count = 0

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: prefix with underscore
def _internal_method():
    pass
```

### 1.3 Type Hints
```python
# Always use type hints
def process_message(message: Message, priority: int = 50) -> bool:
    pass

# Use Optional for nullable
from typing import Optional
def get_user(user_id: str) -> Optional[User]:
    pass

# Use list, dict (Python 3.10+)
def get_messages() -> list[Message]:
    pass
```

### 1.4 Docstrings
```python
def calculate_priority(message: Message, sender_weight: float) -> int:
    """
    Calculate message priority score.
    
    Args:
        message: The message to score
        sender_weight: Weight of the sender (0-100)
    
    Returns:
        Priority score from 0 to 100
    
    Raises:
        ValueError: If sender_weight is out of range
    """
    pass
```

---

## 2. Async Patterns

### 2.1 Always Use Async for I/O
```python
# ✅ Correct
async def fetch_emails():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Wrong - blocking I/O
def fetch_emails():
    response = requests.get(url)  # Blocks!
    return response.json()
```

### 2.2 Concurrent Execution
```python
# Run multiple tasks concurrently
async def fetch_all():
    gmail_task = asyncio.create_task(gmail.fetch())
    slack_task = asyncio.create_task(slack.fetch())
    
    gmail_msgs, slack_msgs = await asyncio.gather(gmail_task, slack_task)
    return gmail_msgs + slack_msgs
```

---

## 3. Error Handling

### 3.1 Use Specific Exceptions
```python
# ✅ Correct
try:
    await agent.authenticate()
except AuthenticationError as e:
    logger.error(f"Auth failed: {e}")
    raise
except NetworkError as e:
    logger.warning(f"Network issue: {e}")
    await retry_with_backoff()

# ❌ Wrong - catching all
try:
    await agent.authenticate()
except Exception:
    pass  # Silent failure!
```

### 3.2 Always Log Errors
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await process()
except Exception as e:
    logger.error(f"Processing failed: {e}", exc_info=True)
    raise
```

---

## 4. Project Structure

### 4.1 Module Organization
```python
# Each module should have:
# 1. Imports (stdlib, third-party, local)
# 2. Constants
# 3. Classes
# 4. Functions
# 5. Main block (if applicable)

# Example:
"""Module docstring."""

# Standard library
import asyncio
from typing import Optional

# Third-party
import httpx

# Local
from core.event_bus import EventBus

# Constants
MAX_RETRIES = 3

# Classes
class MyClass:
    pass

# Functions
def my_function():
    pass

# Main
if __name__ == "__main__":
    pass
```

---

## 5. Testing Standards

### 5.1 Test Naming
```python
# test_<module>_<function>_<scenario>
def test_priority_scorer_high_urgency_returns_high_score():
    pass

def test_gmail_agent_fetch_returns_messages():
    pass
```

### 5.2 Test Structure
```python
def test_something():
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

---

## 6. Git Conventions

### 6.1 Commit Messages
```
<type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance

Examples:
feat: Add Gmail OAuth authentication
fix: Handle empty message list
docs: Update README with setup instructions
```

### 6.2 Branch Naming
```
feature/<name>    - New features
bugfix/<name>     - Bug fixes
refactor/<name>   - Refactoring

Examples:
feature/gmail-agent
bugfix/notification-crash
refactor/event-bus
```
