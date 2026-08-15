# Session Store, Memory, Retrieval, RAG and Context Architecture

## Why this exists

A production AI application separates **persistent information sources** from the **bounded context sent to the LLM**.

The application may retain a complete conversation record while separately maintaining durable memory, retrieving enterprise knowledge through RAG, and querying live enterprise systems through tools/APIs. The context layer then selects and assembles only the information needed for the current model invocation.

## Canonical enterprise mental model — detailed

```text
                                      ┌─────────────────────┐
                                      │        USER         │
                                      │                     │
                                      │  Current Request    │
                                      └──────────┬──────────┘
                                                 │
                                                 ▼
                              ┌──────────────────────────────┐
                              │      API / CHAT LAYER        │
                              │                              │
                              │ • Receive request            │
                              │ • Authentication             │
                              │ • Request metadata            │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │       SESSION MANAGER        │
                              │                              │
                              │ • user_id                    │
                              │ • conversation_id            │
                              │ • session state              │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                    ┌────────────────────────────────────────────────┐
                    │              CONVERSATION STORE                │
                    │                                                │
                    │                 CHAT HISTORY                   │
                    │                                                │
                    │                  "What happened?"              │
                    │                                                │
                    │ • Raw user messages                            │
                    │ • Raw assistant messages                        │
                    │ • Timestamps                                    │
                    │ • Conversation metadata                         │
                    │ • Complete conversation record                  │
                    └────────────────────────┬───────────────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │     ORCHESTRATOR / ROUTER    │
                              │                              │
                              │ "What capability/source     │
                              │  does this request require?"│
                              └──────────────┬───────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
        │   CHAT HISTORY    │    │      MEMORY       │    │       RAG         │
        │                   │    │                   │    │                   │
        │ "What happened?" │    │ "Remember this"   │    │ "What does the    │
        │                   │    │                   │    │  enterprise know?"│
        │ • Recent turns    │    │ • Preferences     │    │                   │
        │ • Old turns       │    │ • Durable facts   │    │ • Documents       │
        │ • Historical      │    │ • Project context │    │ • Policies        │
        │   conversation    │    │ • Goals           │    │ • SOPs            │
        └─────────┬─────────┘    └─────────┬─────────┘    │ • Knowledge bases│
                  │                        │              └─────────┬─────────┘
                  │                        │                        │
                  ▼                        ▼                        ▼
        ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
        │ HISTORY RETRIEVAL │    │ MEMORY RETRIEVAL  │    │  RAG RETRIEVAL    │
        │                   │    │                   │    │                   │
        │ • Recent window   │    │ • Relevant facts  │    │ • Query           │
        │ • Historical      │    │ • Relevant state  │    │ • Retrieve        │
        │   search          │    │ • Relevant prefs  │    │ • Filter          │
        │ • Relevance       │    │ • Relevance       │    │ • Rank            │
        │   ranking         │    │   ranking         │    │ • Rerank          │
        └─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘
                  │                        │                        │
                  └────────────────────────┼────────────────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────────┐
                              │        TOOLS / APIs          │
                              │                              │
                              │ • SQL                        │
                              │ • REST APIs                  │
                              │ • Enterprise applications   │
                              │ • Live operational systems  │
                              │ • Actions / transactions    │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │       CONTEXT MANAGER        │
                              │                              │
                              │ "What information should    │
                              │  the LLM actually see?"     │
                              │                              │
                              │ • Task relevance             │
                              │ • Recency                    │
                              │ • Source authority            │
                              │ • Conversation continuity    │
                              │ • Information priority       │
                              │ • Token budget                │
                              │ • Latency / cost              │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │       CONTEXT BUILDER        │
                              │                              │
                              │ Assemble final model input: │
                              │                              │
                              │ • System instructions       │
                              │ • Relevant chat history     │
                              │ • Memory                     │
                              │ • RAG results                │
                              │ • Tool results               │
                              │ • Current request            │
                              │                              │
                              │ Apply:                       │
                              │ • Ordering                   │
                              │ • Filtering                  │
                              │ • Formatting                 │
                              │ • Token limits               │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │             LLM              │
                              │                              │
                              │ • Understand context         │
                              │ • Reason                     │
                              │ • Generate response          │
                              │ • Produce structured output │
                              │ • Request tool calls         │
                              └──────────────┬───────────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              │                             │
                              ▼                             ▼
                  ┌────────────────────┐       ┌──────────────────────┐
                  │    FINAL ANSWER    │       │      TOOL CALL       │
                  │                    │       │                      │
                  │ Return response    │       │ Requested action     │
                  │ to user            │       │ / external operation  │
                  └─────────┬──────────┘       └──────────┬───────────┘
                            │                             │
                            │                             ▼
                            │                  ┌──────────────────────┐
                            │                  │  ENTERPRISE SYSTEM   │
                            │                  │                      │
                            │                  │ SQL / API / Service  │
                            │                  └──────────┬───────────┘
                            │                             │
                            │                             ▼
                            │                  ┌──────────────────────┐
                            │                  │     TOOL RESULT      │
                            │                  └──────────┬───────────┘
                            │                             │
                            │                             ▼
                            │                  ┌──────────────────────┐
                            │                  │   ORCHESTRATOR /     │
                            │                  │   CONTEXT MANAGER    │
                            │                  │                      │
                            │                  │ Re-evaluate context  │
                            │                  │ and continue workflow│
                            │                  └──────────┬───────────┘
                            │                             │
                            │                             ▼
                            │                            LLM
                            │                             │
                            │                             ▼
                            │                       FINAL ANSWER
                            │                             │
                            └─────────────────────────────┘
                                                          │
                                                          ▼
                                                         USER
```

## Information-source layer

```text
                         INFORMATION SOURCES
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
          ▼                       ▼                        ▼
 ┌────────────────┐      ┌────────────────┐       ┌────────────────┐
 │  CHAT HISTORY  │      │     MEMORY     │       │      RAG       │
 │                │      │                │       │                │
 │ "What happened?"│     │ "Remember this"│       │ "What does the │
 │                │      │                │       │ enterprise     │
 │ Raw conversation│     │ Durable facts  │       │ know?"         │
 │ Recent turns   │      │ Preferences    │       │                │
 │ Historical turns│     │ Goals          │       │ Documents      │
 └───────┬────────┘      │ Project state  │       │ Policies       │
         │               └───────┬────────┘       │ SOPs           │
         ▼                       ▼                │ Knowledge base │
 ┌────────────────┐      ┌────────────────┐       └───────┬────────┘
 │History Retrieval│     │Memory Retrieval│               │
 └───────┬────────┘      └───────┬────────┘               │
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ CONTEXT       │
                         │ MANAGER       │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ CONTEXT       │
                         │ BUILDER       │
                         └───────┬───────┘
                                 │
                                 ▼
                                LLM
```

Tools sit alongside these information sources because they are fundamentally different:

```text
RAG
 │
 └── "What does the enterprise know?"
       → Retrieve knowledge

TOOLS
 │
 └── "What is live / what can we do?"
       → Read live data
       → Execute actions
       → Change enterprise state
```

## Responsibility chain

```text
SESSION MANAGER
    │
    └── "Which conversation?"

ROUTER / ORCHESTRATOR
    │
    └── "Which capability/source?"

RETRIEVAL
    │
    └── "What might be relevant?"

CONTEXT MANAGER
    │
    └── "What should the LLM see?"

CONTEXT BUILDER
    │
    └── "How do we package it?"

LLM
    │
    └── "What should I generate / what action should I request?"

TOOLS
    │
    └── "Read/change the external system"

AGENT / ORCHESTRATOR
    │
    └── "What should happen next?"
```

## The four primary information sources

### 1. Chat History — "What happened?"

The conversation store is the raw record of interaction events. Typical fields include:

```text
conversation_id
message_id
role
content
timestamp
metadata
```

Chat history is useful for conversational continuity, audit/history requirements, debugging, analytics, and future retrieval. It is the **record**, not automatically the complete model context.

### 2. Structured Memory — "What should we remember?"

Memory is **durable information derived from interactions**, stored separately from raw chat history when it is useful across turns or sessions.

Typical categories:

```text
User preferences
Project context
Long-lived facts
Goals
Important application state
Entities / relationships
```

Examples:

```text
response_style = concise
project = inventory AI assistant
platform = Azure Databricks
goal = build enterprise AI agent
```

Not every message becomes memory. A question such as "What is RAG?" normally does not need to become durable memory, while a stable preference such as "I prefer concise technical answers" may.

**Memory is derived information, not automatically the authoritative source of truth.** If memory conflicts with an authoritative enterprise system or approved document, the authoritative source should win.

### 3. RAG — "What does the enterprise know?"

RAG is a retrieval-and-generation architecture. In enterprise applications it commonly retrieves information from approved company knowledge sources such as:

```text
Policies
SOPs
Technical documentation
Product documentation
Internal FAQs
Knowledge bases
Architecture documents
Business rules
Data catalog documentation
```

Typical pipeline:

```text
Enterprise sources
      ↓
Parsing / ingestion
      ↓
Chunking
      ↓
Embedding
      ↓
Vector / hybrid index
      ↓
Retrieval
      ↓
Ranking / reranking
      ↓
Relevant chunks
      ↓
Context
      ↓
LLM
```

RAG is **not simply "company data"** and it is not the final answer generator. Its primary role is to retrieve relevant external knowledge that can ground the model response.

### 4. Tools / SQL / APIs — "What is live, and what can we do?"

Tools connect the AI application to operational systems and actions.

Examples:

```text
SQL database
REST API
Inventory service
Ticketing system
Workflow service
Replenishment API
Python execution
```

A useful distinction:

```text
RAG   → What does the enterprise know?
Tool  → What is happening now / what can the system do?
```

## The three responsibilities that are easy to confuse

### Router / Orchestrator

**Question:** "What capability or source do I need?"

It may decide that a request needs:

```text
General LLM
RAG
Memory
SQL
API
Multiple tools
Agent workflow
```

### Context Manager

**Question:** "What information should the LLM see for this request?"

It selects the useful pieces from the available sources while considering:

```text
Task relevance
Recency
Source authority
Conversation continuity
Token budget
Latency / cost
```

### Context Builder

**Question:** "How do I assemble the selected information into the model request?"

It packages items such as:

```text
System instructions
Relevant conversation
Memory
RAG results
Tool results
Current request
```

and enforces ordering, filtering, formatting, and token limits.

### Golden rule

> **Router decides what capability/source is needed. Context Manager decides what information the LLM should see. Context Builder assembles that information into the model request. The LLM reasons and generates using the supplied context.**

## How the sources fit together

```text
                    INFORMATION SOURCES
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    CHAT HISTORY        MEMORY             RAG
    "What happened?"  "Remember this"  "What does the
                                       enterprise know?"
          │                │                │
          └────────────────┼────────────────┘
                           │
                         TOOLS
                 "What is live / what
                    can we do?"
                           │
                           ▼
                  CONTEXT MANAGER
                           │
                           ▼
                    CONTEXT BUILDER
                           │
                           ▼
                          LLM
```

## Retrieval is not the same as context

This distinction is critical:

```text
Storage
  ↓
What exists?

Retrieval
  ↓
What might be relevant?

Context Manager
  ↓
What should the LLM see?

Context Builder
  ↓
How do we package it?

LLM
  ↓
What answer/action should be produced?
```

The application should not assume that everything stored must be retrieved, or that everything retrieved must be sent to the LLM.

## Current learning implementation

Path:

```text
01_ai_fundamentals/01_first_llm/
├── app.py
├── database.py
└── conversation_store.db   # generated locally; not committed
```

SQLite is being used as a transparent learning implementation. The abstraction can later map to PostgreSQL, managed NoSQL, Redis/session infrastructure, or managed agent-memory services depending on production requirements.

### Current database model

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

## Learning progression

We are intentionally building the architecture in layers:

```text
1. Persistent conversation store                    ✅
        ↓
2. Context Manager V1                              ← NEXT
   Recent turns + summary + token budget
        ↓
3. Deliberately test the limitation
        ↓
4. Historical conversation retrieval
        ↓
5. Structured memory
        ↓
6. Embeddings
        ↓
7. Vector / hybrid search
        ↓
8. RAG
        ↓
9. Tools / SQL / APIs
        ↓
10. Router / agent orchestration
        ↓
11. Evaluation / guardrails / security / observability
        ↓
12. Enterprise AI Agent
```

## Core principles

> **The conversation store is the record; the model context is the working set.**

> **Chat history records what happened. Memory preserves useful durable information. RAG retrieves enterprise knowledge. Tools access live systems and perform actions.**

> **Router decides what capability/source is needed. Context Manager decides what information the LLM should see. Context Builder assembles it.**

These distinctions are foundational AI Engineering concepts and should remain consistent throughout the masterclass.
