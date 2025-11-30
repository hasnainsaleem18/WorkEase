# LangChain & RAG Integration Guide

## Overview

This document describes how to upgrade AUTOCOM from the simple SQLite-based memory store to advanced context management using **LangChain** or **RAG (Retrieval-Augmented Generation)**.

**Current Status**: Architecture is prepared and abstracted, but NOT implemented.

**When to Upgrade**: When you need:
- More sophisticated conversation memory
- Search through large document collections
- Better long-term context retention
- Integration with external knowledge bases

---

## Architecture Preparation (✅ DONE)

### 1. Context Provider Protocol

We've created `core/context_provider.py` which defines the interface that ANY context system must implement:

```python
class ContextProvider(Protocol):
    async def initialize() -> None
    async def store_interaction(intent, response, embedding) -> None
    async def get_recent_context(limit, context_id) -> list[dict]
    async def search_similar(query_embedding, k) -> list[dict]
    async def clear_session(session_id) -> None
    async def close() -> None
```

### 2. Current Implementation

`database/memory.py` (MemoryStore) implements this protocol using:
- SQLite for structured storage
- NumPy for vector embeddings
- Simple cosine similarity search

### 3. Orchestrator Integration

The orchestrator uses the protocol, not the concrete class:

```python
# In core/orchestrator.py
def __init__(self, llm, memory: ContextProvider, event_bus):
    self.memory = memory  # Can be ANY implementation!
```

This means you can swap implementations without changing orchestrator code.

---

## Upgrade Option 1: LangChain Memory

### What is LangChain?

LangChain provides sophisticated memory management for LLM applications:
- **ConversationBufferMemory**: Stores full conversation history
- **ConversationSummaryMemory**: Summarizes old conversations
- **ConversationBufferWindowMemory**: Keeps last N messages
- **VectorStoreRetrieverMemory**: Semantic search over history

### When to Use

- You want automatic conversation summarization
- You need better context window management
- You want to integrate with LangChain agents/chains
- You need more sophisticated memory strategies

### Implementation Steps

#### Step 1: Install Dependencies

```bash
pip install langchain langchain-community langchain-ollama
```

Update `requirements.txt`:
```
langchain>=0.1.0
langchain-community>=0.1.0
langchain-ollama>=0.1.0
```

#### Step 2: Create LangChain Provider

Create `database/langchain_memory.py`:

```python
from typing import Any, Optional
import numpy as np
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from core.context_provider import BaseContextProvider


class LangChainMemoryProvider(BaseContextProvider):
    """LangChain-based memory provider."""
    
    def __init__(self, llm_model: str = "llama3.2:3b"):
        self.llm = OllamaLLM(model=llm_model)
        self.memory = ConversationBufferMemory(
            llm=self.llm,
            max_token_limit=2000,
            return_messages=True
        )
    
    async def initialize(self) -> None:
        """Initialize LangChain memory."""
        pass  # LangChain handles initialization
    
    async def store_interaction(
        self, intent: Any, response: str, embedding: Optional[np.ndarray] = None
    ) -> None:
        """Store interaction in LangChain memory."""
        self.memory.save_context(
            {"input": intent.raw_input},
            {"output": response}
        )
    
    async def get_recent_context(
        self, limit: int = 10, context_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Get recent context from LangChain."""
        messages = self.memory.load_memory_variables({})
        # Convert LangChain format to our format
        history = messages.get("history", [])
        return [
            {
                "user_input": msg.content if hasattr(msg, 'content') else str(msg),
                "intent": {},
                "response": ""
            }
            for msg in history[-limit:]
        ]
    
    async def search_similar(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> list[dict[str, Any]]:
        """Semantic search (requires vector store)."""
        # Implement with LangChain VectorStoreRetrieverMemory
        return []
    
    async def clear_session(self, session_id: str) -> None:
        """Clear LangChain memory."""
        self.memory.clear()
    
    async def close(self) -> None:
        """Cleanup."""
        pass
```

#### Step 3: Update Configuration

Add to `config/config.yaml`:

```yaml
memory:
  provider: "langchain"  # or "simple" for SQLite
  langchain:
    memory_type: "buffer"  # buffer, summary, window
    max_tokens: 2000
    summarize_old: true
```

#### Step 4: Update Main Application

In `core/main.py`:

```python
from config import load_config

config = load_config()

if config.memory.provider == "langchain":
    from database.langchain_memory import LangChainMemoryProvider
    memory = LangChainMemoryProvider(llm_model=config.llm.model)
else:
    from database.memory import MemoryStore
    memory = MemoryStore(db_path=config.memory.db_path)

await memory.initialize()
orchestrator = Orchestrator(llm, memory, event_bus)
```

### Benefits of LangChain

✅ Automatic conversation summarization
✅ Better context window management
✅ Integration with LangChain ecosystem
✅ Multiple memory strategies
✅ Built-in token counting

### Drawbacks

❌ More dependencies (heavier)
❌ Slightly slower than raw SQLite
❌ More complex debugging
❌ Requires understanding LangChain concepts

---

## Upgrade Option 2: RAG (Retrieval-Augmented Generation)

### What is RAG?

RAG combines:
1. **Vector Database** (Chroma, Pinecone, Weaviate) - Stores embeddings
2. **Embedding Model** (sentence-transformers) - Creates vectors
3. **Retrieval** - Finds relevant context from large collections
4. **Generation** - LLM uses retrieved context to answer

### When to Use

- You have large document collections (emails, Slack history)
- You need to search months/years of history
- You want semantic search over all communications
- You need to answer questions about past conversations

### Implementation Steps

#### Step 1: Install Dependencies

```bash
pip install langchain chromadb sentence-transformers
```

Update `requirements.txt`:
```
langchain>=0.1.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

#### Step 2: Create RAG Provider

Create `database/rag_memory.py`:

```python
from typing import Any, Optional
import numpy as np
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.context_provider import BaseContextProvider


class RAGContextProvider(BaseContextProvider):
    """RAG-based context provider with vector database."""
    
    def __init__(
        self,
        persist_directory: str = "memory/chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
    
    async def initialize(self) -> None:
        """Initialize Chroma vector database."""
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    async def store_interaction(
        self, intent: Any, response: str, embedding: Optional[np.ndarray] = None
    ) -> None:
        """Store interaction in vector database."""
        # Combine user input and response
        text = f"User: {intent.raw_input}\nAssistant: {response}"
        
        # Add metadata
        metadata = {
            "timestamp": str(intent.timestamp),
            "action": intent.action,
            "target": intent.target,
            "context_id": intent.context_id
        }
        
        # Store in Chroma
        self.vector_store.add_texts(
            texts=[text],
            metadatas=[metadata]
        )
    
    async def get_recent_context(
        self, limit: int = 10, context_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Get recent context (query by metadata)."""
        # Query Chroma with metadata filter
        results = self.vector_store.similarity_search(
            query="",
            k=limit,
            filter={"context_id": context_id}
        )
        
        return [
            {
                "user_input": doc.page_content.split("User: ")[1].split("\n")[0],
                "response": doc.page_content.split("Assistant: ")[1],
                "intent": {},
                "timestamp": doc.metadata.get("timestamp")
            }
            for doc in results
        ]
    
    async def search_similar(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> list[dict[str, Any]]:
        """Semantic search using vector similarity."""
        # Convert query to text (or use embedding directly)
        results = self.vector_store.similarity_search_by_vector(
            embedding=query_embedding.tolist(),
            k=k
        )
        
        return [
            {
                "similarity": 1.0,  # Chroma returns sorted by similarity
                "user_input": doc.page_content,
                "intent": {},
                "response": "",
                "timestamp": doc.metadata.get("timestamp")
            }
            for doc in results
        ]
    
    async def clear_session(self, session_id: str) -> None:
        """Clear session from vector database."""
        # Delete by metadata filter
        self.vector_store.delete(
            filter={"context_id": session_id}
        )
    
    async def close(self) -> None:
        """Persist and cleanup."""
        if self.vector_store:
            self.vector_store.persist()
```

#### Step 3: Update Configuration

Add to `config/config.yaml`:

```yaml
memory:
  provider: "rag"  # simple, langchain, or rag
  rag:
    vector_db: "chroma"  # chroma, pinecone, weaviate
    persist_directory: "memory/chroma_db"
    embedding_model: "all-MiniLM-L6-v2"
    chunk_size: 500
```

#### Step 4: Add RAG Query Interface

Create `core/rag_query.py` for advanced queries:

```python
class RAGQueryEngine:
    """Advanced query interface for RAG system."""
    
    def __init__(self, context_provider: RAGContextProvider, llm):
        self.context_provider = context_provider
        self.llm = llm
    
    async def query_history(self, question: str) -> str:
        """
        Answer questions about conversation history.
        
        Example: "What emails did I receive from John last week?"
        """
        # 1. Retrieve relevant context
        query_embedding = self._embed_query(question)
        relevant_docs = await self.context_provider.search_similar(
            query_embedding, k=10
        )
        
        # 2. Build context for LLM
        context = "\n\n".join([
            f"- {doc['user_input']}: {doc['response']}"
            for doc in relevant_docs
        ])
        
        # 3. Generate answer
        prompt = f"""Based on this conversation history:
{context}

Answer this question: {question}"""
        
        answer = await self.llm.generate(prompt)
        return answer
```

### Benefits of RAG

✅ Search through massive history (months/years)
✅ Semantic search (meaning-based, not keyword)
✅ Answer questions about past conversations
✅ Scalable to millions of messages
✅ Persistent vector storage

### Drawbacks

❌ More complex setup
❌ Requires vector database
❌ Higher storage requirements
❌ Slower than simple SQLite
❌ Needs good embedding model

---

## Comparison Matrix

| Feature | Simple SQLite | LangChain | RAG |
|---------|--------------|-----------|-----|
| **Complexity** | ⭐ Simple | ⭐⭐ Medium | ⭐⭐⭐ Complex |
| **Performance** | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡ Slower |
| **Memory Usage** | 💾 Low | 💾💾 Medium | 💾💾💾 High |
| **Context Window** | 10-20 msgs | 50-100 msgs | Unlimited |
| **Semantic Search** | ✅ Basic | ✅ Good | ✅✅ Excellent |
| **Summarization** | ❌ No | ✅ Yes | ✅ Yes |
| **Large History** | ❌ Limited | ⚠️ OK | ✅ Excellent |
| **Dependencies** | Minimal | Medium | Many |
| **Weak PC Friendly** | ✅ Yes | ⚠️ OK | ❌ No |

---

## Recommended Upgrade Path

### Phase 1: MVP (Current - Simple SQLite)
- ✅ Use `MemoryStore` (database/memory.py)
- ✅ Works great for recent context (10-20 messages)
- ✅ Fast and lightweight
- ✅ Perfect for weak PC

### Phase 2: Better Context (LangChain)
**When**: You need better conversation management
**Upgrade**: Switch to `LangChainMemoryProvider`
**Effort**: 2-3 hours
**Benefits**: Automatic summarization, better context

### Phase 3: Advanced Search (RAG)
**When**: You have months of history to search
**Upgrade**: Switch to `RAGContextProvider`
**Effort**: 1-2 days
**Benefits**: Semantic search, answer questions about history

---

## Configuration Examples

### Simple (Current)

```yaml
# config/config.yaml
memory:
  provider: "simple"
  db_path: "memory/context.db"
  retention_days: 30
  embedding_model: "all-MiniLM-L6-v2"
```

### LangChain

```yaml
memory:
  provider: "langchain"
  langchain:
    memory_type: "summary"  # buffer, summary, window
    max_tokens: 2000
    llm_model: "llama3.2:3b"
```

### RAG

```yaml
memory:
  provider: "rag"
  rag:
    vector_db: "chroma"
    persist_directory: "memory/chroma_db"
    embedding_model: "all-MiniLM-L6-v2"
    chunk_size: 500
    search_k: 10
```

---

## Testing the Upgrade

### Test 1: Basic Context Retrieval

```python
# Test any provider implementation
async def test_context_provider(provider: ContextProvider):
    await provider.initialize()
    
    # Store interaction
    intent = Intent(
        action="fetch",
        target="gmail",
        parameters={},
        confidence=0.9,
        context_id="test",
        raw_input="Check my emails"
    )
    await provider.store_interaction(intent, "Found 5 emails")
    
    # Retrieve context
    context = await provider.get_recent_context(limit=10)
    assert len(context) > 0
    assert context[0]["user_input"] == "Check my emails"
    
    await provider.close()
```

### Test 2: Semantic Search

```python
async def test_semantic_search(provider: ContextProvider):
    # Store multiple interactions
    # ... store various emails, slack messages ...
    
    # Search for similar
    query_embedding = embed_text("emails from John")
    results = await provider.search_similar(query_embedding, k=5)
    
    assert len(results) > 0
    assert "john" in results[0]["user_input"].lower()
```

---

## Migration Script

When you're ready to upgrade, use this migration script:

```python
# scripts/migrate_to_langchain.py
import asyncio
from database.memory import MemoryStore
from database.langchain_memory import LangChainMemoryProvider


async def migrate():
    """Migrate from SQLite to LangChain."""
    # Load old data
    old_store = MemoryStore("memory/context.db")
    await old_store.initialize()
    
    # Get all history
    history = await old_store.get_recent_context(limit=1000)
    
    # Create new provider
    new_store = LangChainMemoryProvider()
    await new_store.initialize()
    
    # Migrate data
    for item in history:
        # Convert to Intent object
        intent = create_intent_from_dict(item)
        await new_store.store_interaction(
            intent, item["response"]
        )
    
    print(f"Migrated {len(history)} interactions")
    
    await old_store.close()
    await new_store.close()


if __name__ == "__main__":
    asyncio.run(migrate())
```

---

## Summary

**Current State**: ✅ Architecture prepared, abstraction layer created

**To Upgrade**:
1. Choose provider (LangChain or RAG)
2. Install dependencies
3. Implement provider class
4. Update configuration
5. Test thoroughly
6. Migrate data (optional)

**Recommendation**: Start with simple SQLite, upgrade to LangChain when needed, consider RAG only for large-scale deployments.

The beauty of this design: **You can upgrade anytime without rewriting the orchestrator!**
