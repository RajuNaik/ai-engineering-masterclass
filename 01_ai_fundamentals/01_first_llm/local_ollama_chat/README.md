# Local Ollama Chat — Persistent History + Short-Term Context

## Purpose

This project is kept separate from the RAG learning path. It demonstrates a local LLM application using Ollama with:

- a locally hosted model
- persistent conversation history in Azure Data Lake Storage Gen2 (ADLS)
- the last 5 chat messages supplied to the model as short-term conversational context
- a persisted conversation summary supplied as additional context
- volatile in-memory context that disappears when the application process stops
- a 7-day retention/cleanup rule for persisted chat history

## Target flow

```text
User Prompt
    |
    v
Python Application
    |
    +--> Load persisted summary
    |
    +--> Load last 5 messages
    |
    +--> Build LLM context
    |
    v
Ollama Local Model
    |
    v
Assistant Response
    |
    +--> Persist user + assistant messages to ADLS
    +--> Update persisted summary
    |
    v
Response to User
```

## Important distinction

This project is intentionally **not RAG**.

```text
Chat History  --> conversational context
Memory        --> persisted useful conversation state / summary
RAG           --> enterprise knowledge retrieval
Tools/APIs    --> external actions or live data
```

The ADLS history is a persistence layer for conversation state. It is not a vector database and is not enterprise knowledge retrieval.

## Local model setup

### 1. Install Ollama

Official Ollama website:

https://ollama.com/

Windows download:

https://ollama.com/download/windows

Download and install Ollama for Windows.

### 2. Verify installation

Open a new terminal and run:

```powershell
ollama --version
```

### 3. Download a local model

Example:

```powershell
ollama pull llama3.2
```

Verify available models:

```powershell
ollama list
```

### 4. Test the model directly

```powershell
ollama run llama3.2
```

Enter a sample prompt such as:

```text
What is context engineering?
```

Exit the interactive session when finished.

## Python environment

From the repository root, use the existing virtual environment or create one:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required packages for the application:

```powershell
pip install ollama azure-identity azure-storage-file-datalake
```

## Azure persistence

The conversation history is persisted in the ADLS Gen2 account used by the masterclass.

Target layout:

```text
ADLS Gen2
└── rag-raw
    └── chat-history
        └── <conversation_id>/
            ├── messages.jsonl
            └── summary.json
```

The exact storage account/container configuration should be supplied through environment/configuration rather than hard-coded secrets.

Authentication should use Microsoft Entra ID through `DefaultAzureCredential` where possible.

## Conversation context policy

For every user request:

1. Identify the conversation.
2. Read the persisted conversation summary.
3. Read the most recent 5 messages.
4. Build the model context from the summary + last 5 messages + current user prompt.
5. Send that context to the local Ollama model.
6. Persist the new user and assistant messages.
7. Update the persisted summary when required.
8. Apply the 7-day history retention rule.

### Why only the last 5 messages?

The purpose is to demonstrate controlled short-term context rather than continuously sending the entire conversation to the LLM. This keeps the prompt smaller while the summary preserves higher-level conversational information.

## Memory lifecycle

There are two different concepts here:

### Process memory

The Python application's in-memory variables contain temporary state only. When the application process closes, this volatile memory disappears.

### Persisted history

ADLS contains the durable conversation history. Restarting the application therefore does **not** delete the persisted history.

### Seven-day cleanup

Persisted conversation history is subject to a 7-day retention rule. The application should remove or archive history older than 7 days according to the implementation used for this exercise.

This is separate from process restart.

## Planned application structure

```text
local_ollama_chat/
├── README.md
├── app.py
├── config.py
├── ollama_client.py
├── chat_history.py
├── memory.py
└── requirements.txt
```

The implementation will be built incrementally so each responsibility is clear.

## Sample interaction

```text
User:
What is RAG?

Application:
1. Load summary
2. Load last 5 messages
3. Build context
4. Call Ollama
5. Persist conversation

Ollama:
<local model response>
```

## What this project teaches

- Running an LLM locally with Ollama
- Calling a local model from Python
- Conversation persistence
- Short-term conversational context
- Summarized conversational memory
- ADLS as a durable conversation-history store
- Difference between volatile application memory and durable storage
- Retention/cleanup of historical conversations
- Why persisted chat history is not the same as RAG

## Deliberately deferred

The following belong to later parts of the AI Engineering masterclass:

- RAG ingestion
- document parsing
- chunking
- embeddings
- vector databases
- hybrid search
- reranking
- tools/API calling
- agent orchestration
- production memory architectures

This project should remain a clean standalone learning exercise before those topics are introduced.
