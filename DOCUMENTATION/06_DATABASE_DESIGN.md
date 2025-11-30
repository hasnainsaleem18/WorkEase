# 🗄️ Database Design Document

## 1. Database Overview

**Database:** SQLite (local file)  
**Location:** `data/autocom.db`  
**Purpose:** Store messages, tasks, preferences, and logs locally

---

## 2. Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  messages   │────<│   tasks     │     │ preferences │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  context    │     │  audit_log  │
└─────────────┘     └─────────────┘
```

---

## 3. Table Definitions

### 3.1 messages
```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,           -- 'gmail' or 'slack'
    sender TEXT NOT NULL,
    sender_email TEXT,
    subject TEXT,
    content TEXT NOT NULL,
    snippet TEXT,                   -- Preview text
    timestamp DATETIME NOT NULL,
    priority INTEGER DEFAULT 50,    -- 0-100
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    raw_data TEXT,                  -- JSON of original
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_source ON messages(source);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_priority ON messages(priority);
```

### 3.2 tasks
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'NORMAL', -- LOW, NORMAL, HIGH, URGENT
    source_message_id TEXT,
    deadline DATETIME,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_message_id) REFERENCES messages(id)
);

CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(is_completed);
```

### 3.3 preferences
```sql
CREATE TABLE preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 sender_weights
```sql
CREATE TABLE sender_weights (
    sender TEXT PRIMARY KEY,
    weight REAL DEFAULT 50.0,       -- 0-100
    reply_count INTEGER DEFAULT 0,
    ignore_count INTEGER DEFAULT 0,
    priority_count INTEGER DEFAULT 0,
    last_interaction DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.5 context
```sql
CREATE TABLE context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_input TEXT NOT NULL,
    intent_json TEXT,
    response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_context_session ON context(session_id);
CREATE INDEX idx_context_timestamp ON context(timestamp);
```

### 3.6 audit_log
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,           -- 'email_sent', 'task_created', etc.
    details TEXT,                   -- JSON
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
```

### 3.7 notification_queue
```sql
CREATE TABLE notification_queue (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    priority INTEGER DEFAULT 50,
    source TEXT,
    scheduled_at DATETIME,
    delivered BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Data Operations

### 4.1 Message Operations
```python
# Insert message
async def insert_message(message: Message) -> None:
    await db.execute("""
        INSERT INTO messages (id, source, sender, subject, content, timestamp, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (message.id, message.source, message.sender, 
          message.subject, message.content, message.timestamp, message.priority))

# Get unread messages
async def get_unread_messages(source: str = None) -> list[Message]:
    query = "SELECT * FROM messages WHERE is_read = FALSE"
    if source:
        query += f" AND source = '{source}'"
    query += " ORDER BY priority DESC, timestamp DESC"
    return await db.fetch_all(query)

# Mark as read
async def mark_read(message_id: str) -> None:
    await db.execute(
        "UPDATE messages SET is_read = TRUE WHERE id = ?",
        (message_id,)
    )
```

### 4.2 Task Operations
```python
# Insert task
async def insert_task(task: Task) -> None:
    await db.execute("""
        INSERT INTO tasks (id, title, description, priority, source_message_id, deadline)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task.id, task.title, task.description, 
          task.priority, task.source_message_id, task.deadline))

# Get pending tasks
async def get_pending_tasks() -> list[Task]:
    return await db.fetch_all("""
        SELECT * FROM tasks 
        WHERE is_completed = FALSE 
        ORDER BY 
            CASE priority 
                WHEN 'URGENT' THEN 1 
                WHEN 'HIGH' THEN 2 
                WHEN 'NORMAL' THEN 3 
                ELSE 4 
            END,
            deadline ASC
    """)

# Complete task
async def complete_task(task_id: str) -> None:
    await db.execute("""
        UPDATE tasks 
        SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (task_id,))
```

### 4.3 Preference Operations
```python
# Get preference
async def get_preference(key: str) -> str:
    result = await db.fetch_one(
        "SELECT value FROM preferences WHERE key = ?", (key,)
    )
    return result['value'] if result else None

# Set preference
async def set_preference(key: str, value: str) -> None:
    await db.execute("""
        INSERT OR REPLACE INTO preferences (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (key, value))
```

---

## 5. Data Maintenance

### 5.1 Auto-Cleanup
```python
async def cleanup_old_data(days: int = 30) -> None:
    """Remove data older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    
    # Delete old messages
    await db.execute(
        "DELETE FROM messages WHERE timestamp < ?", (cutoff,)
    )
    
    # Delete old context
    await db.execute(
        "DELETE FROM context WHERE timestamp < ?", (cutoff,)
    )
    
    # Delete old audit logs (keep 90 days)
    audit_cutoff = datetime.now() - timedelta(days=90)
    await db.execute(
        "DELETE FROM audit_log WHERE timestamp < ?", (audit_cutoff,)
    )
```

### 5.2 Database Backup
```python
async def backup_database(backup_path: str) -> None:
    """Create database backup."""
    import shutil
    shutil.copy('data/autocom.db', backup_path)
```

---

## 6. Indexes Summary

| Table | Index | Columns |
|-------|-------|---------|
| messages | idx_messages_source | source |
| messages | idx_messages_timestamp | timestamp |
| messages | idx_messages_priority | priority |
| tasks | idx_tasks_priority | priority |
| tasks | idx_tasks_completed | is_completed |
| context | idx_context_session | session_id |
| context | idx_context_timestamp | timestamp |
| audit_log | idx_audit_timestamp | timestamp |
