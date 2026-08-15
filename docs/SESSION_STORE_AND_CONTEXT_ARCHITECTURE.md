# Session Store and Context Architecture

## Why this exists

A production AI application separates **persistent conversation history** from the **bounded context sent to the LLM**.

The application may retain a complete conversation record for continuity, audit, analytics, and future retrieval, while the context engine selects only the information needed for the current model invocation.

## Canonical pattern

```text
                         USER
                          │
                          ▼
                 ┌─────────────────┐
                 │ Session Manager │
                 └────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Conversation DB  │
                │ Raw Chat History │
                └────────┬─────────┘
                         │
                         ▼
                 ┌─────────────────┐
                 │ Context Engine  │
                 └────────┬────────┘
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
     Recent turns    Compaction        Structured
                      / summary          memory
          │               │                │
          └───────────────┼────────────────┘
                          │
                          ▼
                  Retrieval / ranking
                          │
                    Token budget
                          │
                          ▼
                    FINAL CONTEXT
                          │
                          ▼
                         LLM
```

## Storage vs context

**Conversation storage:** what the application retains.

**Model context:** what the application chooses to send for one model invocation.

These are deliberately different:

```text
500 stored messages
        ↓
Context selection
        ↓
Recent + summary + relevant memory + task-specific retrieval
        ↓
Maybe 20 useful messages/chunks
        ↓
LLM
```

Never assume that the model needs the entire conversation simply because the application has it.

## Current learning implementation

Path:

```text
01_ai_fundamentals/01_first_llm/
├── app.py
├── database.py
└── conversation_store.db   # generated locally; not committed
```

SQLite is being used as a transparent learning implementation. The abstraction can later map to PostgreSQL, a managed NoSQL store, Redis/session infrastructure, or a managed agent-memory service depending on production requirements.

### Database model

```text
conversations
────────────────────────────
conversation_id  PRIMARY KEY
created_at
updated_at
summary
summary_through_message_id

messages
────────────────────────────
message_id       PRIMARY KEY
conversation_id  FOREIGN KEY
role
content
created_at
```

## Context policy used in the lab

The current implementation deliberately keeps:

- the full raw conversation in SQLite;
- a bounded recent-message window for model context;
- an LLM-generated rolling summary for older context;
- summary metadata so already-compacted messages are not repeatedly summarized.

This is a **learning baseline**, not the final enterprise memory architecture.

## Why summary is not source of truth

A summary is LLM-generated derived information. It may omit, distort, or misrepresent details. Authoritative enterprise facts should remain recoverable from the underlying enterprise record/document/database.

```text
Enterprise source of truth
        ≠
LLM-generated summary
        ≠
LLM-generated answer
```

## Enterprise evolution

The learning implementation will evolve toward:

```text
Raw conversation store
        ↓
Session state
        ↓
Recent context
        +
Compaction
        +
Structured memory
        +
Semantic retrieval
        +
RAG
        +
Tool/API results
        ↓
Context engine
        ↓
LLM / agent
```

### Core principle

> **The conversation store is the record; the model context is the working set.**

This separation is a foundational AI Engineering concept and should be preserved throughout the masterclass.
