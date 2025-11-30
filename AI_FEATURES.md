# 🧠 WorkEase AI Features

WorkEase integrates advanced local AI capabilities to streamline your communication workflow. This document details the AI-powered features currently implemented.

## 🌟 Key Features

### 1. Intelligent Message Summarization
The system automatically analyzes incoming messages from Slack (and other sources) to provide concise, actionable summaries.

- **Privacy-First**: Uses local/cloud Ollama models, ensuring data privacy.
- **Context-Aware**: Summaries focus on intent and action items, stripping away unnecessary metadata.
- **Smart Formatting**: 
  - Senders are referred to generically (e.g., "The sender") to keep summaries objective.
  - Channel join notifications are simplified.

### 2. Automated Task Extraction
Beyond simple summarization, the AI classifies every message into actionable categories to help you prioritize:

| Category | Description | Action |
|----------|-------------|--------|
| **Smart Draft** 📝 | Requires a thoughtful, composed response. | AI will suggest a draft reply. |
| **Auto Reply** 🤖 | Needs a simple acknowledgement. | Quick replies like "Noted" or "Thanks". |
| **Simple Reply** ℹ️ | Informational only. | No specific action required. |
| **File Attachment** 📎 | Sender is requesting a file. | Triggers file attachment workflow. |

### 3. Robust Queue Processing
To ensure reliability and prevent system overload, WorkEase uses a sophisticated **Queue-Based Architecture**:
- **Controlled Concurrency**: Processes messages in small batches (2 at a time) to respect API rate limits.
- **Stability**: Prevents "overwhelmed" errors even when receiving 50+ messages simultaneously.
- **Background Processing**: All AI operations happen in background threads, keeping the UI responsive.

### 4. Interactive UI
- **Clean Table View**: Shows only the concise summary in the main inbox to reduce clutter.
- **Detailed Analysis**: Click on any summary to open a beautiful, styled dialog showing the full AI analysis, including the Task Classification and reasoning.
- **Visual Cues**: Hover effects and tooltips guide user interaction.

## 🛠️ Technical Setup

### Requirements
- **Ollama**: Must be installed and running.
- **Model**: Currently configured to use `gpt-oss:120b-cloud` for optimal performance (can be switched to local models like `qwen3:0.6b`).

### Configuration
The AI service is configured in `UI/autoreturn_app.py`:
```python
self.ollama_service = OllamaService(model_name="gpt-oss:120b-cloud")
self.queue_summary_generator = QueueSummaryGenerator(self.ollama_service, max_concurrent=2)
```

## 🚀 Usage

1. **Start the Application**:
   ```bash
   ./run.sh
   ```

2. **Automatic Processing**:
   - Connect your accounts (e.g., Slack).
   - New messages are automatically added to the processing queue.
   - Summaries appear in real-time as they are generated.

3. **Manual Trigger**:
   - Click the **"🤖 Generate Summaries"** button to re-process all messages in your inbox.

4. **View Details**:
   - Click on any summary in the "AI Summary" column to view the full Task Classification.
