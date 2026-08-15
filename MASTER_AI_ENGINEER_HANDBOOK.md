# Master AI Engineer — Enterprise AI Engineering Handbook

> Practical, enterprise-first learning path. We build working systems first, then introduce the theory needed to understand and productionize them.

## Course Goal

Build the skills to design, build, evaluate, secure, deploy, and operate enterprise AI systems around existing foundation models — culminating in an enterprise-grade agentic AI capstone.

The target is **Enterprise AI Engineer**: deep enough LLM understanding to reason about model behavior, with the majority of practical work focused on applications, RAG, context engineering, tools, agents, evaluation, security, observability, and production architecture.

## Learning Method

For every major topic:
1. Concept
2. Why it exists
3. Architecture
4. Practical code
5. Hands-on testing
6. Real-world enterprise scenario
7. Enterprise reality checkpoint
8. Mastery check

Interview preparation is reserved for the end of the complete course.

---

# 1. Foundations

## AI → ML → Deep Learning → Generative AI → Agentic AI

- **AI:** broad field of intelligent systems.
- **ML:** systems learn patterns from data.
- **Deep Learning:** ML based primarily on multi-layer neural networks.
- **Generative AI:** models capable of generating text, code, images, audio, etc.
- **Agentic AI:** systems that use models to decide, use tools, observe results, and continue through a workflow.

Practical distinction:

```text
Prediction → ML
Image understanding → Deep Learning
Knowledge-grounded answer → LLM + RAG
System that decides and performs actions → Agentic AI
```

# 2. Existing LLM vs AI Engineer — Exact Boundary

This is a permanent mental model for the course.

```text
                         OUR ENTERPRISE AI APPLICATION
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Context Builder │  ← AI ENGINEER
                         └────────┬────────┘
                                  │
                    messages / prompt / context
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │     MODEL RUNTIME/API    │
                    │                          │
                    │      Tokenizer           │  ← EXISTING
                    │         ↓                │
                    │      Token IDs           │  ← EXISTING
                    │         ↓                │
                    │    ┌──────────────┐       │
                    │    │     LLM      │       │  ← EXISTING
                    │    │ Transformer  │       │
                    │    │ Attention    │       │
                    │    │ Weights      │       │
                    │    └──────┬───────┘       │
                    │           ↓               │
                    │     Generated Tokens     │  ← EXISTING
                    │           ↓               │
                    │       Detokenize         │  ← EXISTING
                    └───────────┬──────────────┘
                                │
                                ▼
                         Generated Response
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Application Logic       │  ← AI ENGINEER
                    │ RAG | Tools | Agents    │
                    │ Memory | Evaluation    │
                    │ Security | Observability│
                    └─────────────────────────┘
```

### Existing / inbuilt LLM scope

When using an existing foundation model such as Llama, the model/runtime provides the model-side capabilities:

- Tokenizer and vocabulary
- Token-to-ID conversion
- Model representations/embeddings inside the network
- Transformer architecture
- Attention mechanisms
- Trained weights
- Next-token prediction
- Text generation
- Detokenization/output conversion

Ollama in our lab is the local model runtime/serving interface; **Ollama is not Llama**.

### AI Engineer scope

The AI Engineer primarily builds and operates the system around the model:

- Application/API layer
- Prompt/message construction
- Context engineering
- Conversation/session state
- RAG
- Document ingestion and chunking
- Retrieval embeddings
- Vector search/database
- Metadata filtering and reranking
- Tool calling
- SQL/API integration
- Routing/orchestration
- Agent orchestration
- Agent memory
- Guardrails
- Evaluation
- Observability/tracing
- Security/authorization integration
- Cost and latency controls
- Deployment and production operations

---

# 3. Tokenization Boundary

The application normally does **not** manually tokenize every request.

```text
AI Engineer application
        │
        │ prompt / messages / context
        ▼
Context engineering / request construction
        │
        ▼
Model API / inference runtime
        │
        ▼
Model-specific tokenizer
        │
        ▼
Token IDs
        │
        ▼
Existing LLM / Transformer
        │
        ▼
Generated tokens
        │
        ▼
Detokenization
        │
        ▼
Text response
```

The AI Engineer still needs token awareness for context limits, token budgets, cost, latency, truncation, summarization, and retrieval design.

# 4. Context Engineering

Useful practical mental model:

```text
                 CONTEXT ENGINEERING
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
        RAG          Conversation      Tools
                     / Memory          Results
          │              │               │
          ▼              ▼               ▼
     Retrieved       Relevant        Tool output
     knowledge       history
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                  CONTEXT BUILDER
                         │
                         ▼
                       LLM
```

**RAG is a major technique used within context engineering, but RAG and context engineering are not synonymous.**

RAG primarily answers: **How do I retrieve relevant external knowledge?**

Context engineering asks: **What information should the model receive, in what form, and at what point in the workflow, so it can perform the current task effectively?**

Possible context sources:
- System instructions
- Current user request
- Recent conversation
- Summarized older conversation
- Structured memory
- RAG results
- Long-term memory
- Tool/API results
- Agent state
- Business rules
- Output constraints

# 5. First Practical Build — Python → Ollama → Llama 3.2

## Environment

- Python 3.11.9
- Repository: `ai-engineering-masterclass`
- Virtual environment: `.venv`
- Ollama 0.32.13
- Local model: Llama 3.2
- Python package: `ollama`

## Application

Path:

```text
01_ai_fundamentals/01_first_llm/app.py
```

Initial architecture:

```text
Python application
      ↓
Ollama runtime
      ↓
Llama 3.2
      ↓
Generated response
      ↓
Python application
```

We intentionally started without LangChain, RAG, agents, vector databases, or other frameworks so the model/application boundary is clear.

## Current application capabilities

- Time-based welcome message
- User input
- Local Llama 3.2 invocation through Ollama
- Continuous chat loop
- Exit command
- In-memory conversation history
- Per-request LLM input/output token metrics
- Context manager using recent-turn selection
- Context compaction/summarization experiment
- Persistent conversation storage and resume by conversation ID

## Current conversation state

```python
messages = []
```

The application can retain the full session in memory, while the context builder decides what is actually sent to the model.

# 6. Tokens — Practical Measurement

A token is a unit used by the model tokenizer to represent text. It is not necessarily equal to one word; tokenization depends on the model/tokenizer.

Our application does not manually convert messages into token IDs. The model/runtime handles tokenization and inference, while our application observes token metrics and manages context.

```text
Python messages[]
        ↓
Context manager
        ↓
Selected context
        ↓
Model runtime / tokenizer
        ↓
LLM
        ↓
Generated tokens
        ↓
Text response
```

Important distinction:

```text
Application message count ≠ token count
```

Token awareness matters for context-window limits, latency, hosted-model cost, RAG budgets, compaction, model selection, and capacity planning.

# 7. Context Window and Token Budget

A model has finite context capacity. The exact available context depends on the model and serving configuration.

```text
More conversation
       ↓
More input tokens
       ↓
Larger context
       ↓
Higher latency / cost
       ↓
Context pressure
```

The AI Engineer's responsibility is to engineer the information sent to the model within an intentional budget.

# 8. Context Manager Evolution

## V1 — Entire history

```text
Full application history → LLM
```

Simple, but context grows indefinitely.

## V2 — Sliding window

```text
Full history
     ↓
Keep latest N turns
     ↓
LLM
```

This reduced token growth but created a deliberate failure: relevant older information disappeared. Our experiment demonstrated that the model could confidently misinterpret `RAG` when the earlier conversational definition was outside the model context.

### Core lesson

```text
Application Memory ≠ Model Context

Recency ≠ Relevance
```

## V3 — Summary + recent turns

```text
Older history
     ↓
LLM summarizer
     ↓
Conversation summary
     +
Recent turns
     ↓
Context Builder
     ↓
LLM
```

This preserves compressed older context, but the summary is itself LLM-generated and therefore **derived information**. It can omit, distort, or misrepresent details.

### Source-of-truth principle

Do not treat an LLM-generated summary as the authoritative source for enterprise facts.

```text
Enterprise source of truth
        ≠
LLM-generated summary
        ≠
LLM-generated answer
```

For authoritative information, the application should be able to retrieve the underlying enterprise record/document when needed.

# 9. Enterprise Context Engineering

A production system should assemble context based on **relevance, reliability, authority, task requirements, and token budget** rather than simply sending the last few messages.

```text
                         USER TASK
                            │
                            ▼
                     CONTEXT ENGINE
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
 Recent conversation   Structured memory     Retrieval / RAG
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                    Context selection
                            │
                       Token budget
                            │
                            ▼
                           LLM
```

Possible context sources include recent chat, summaries, structured application state, relevant enterprise documents, database results, tool outputs, business rules, and agent state.

### Important rule

**Do not retrieve enterprise data blindly before every LLM call.** Instead, the application should determine what the task requires.

Examples:

```text
General concept question
        ↓
LLM may answer directly
```

```text
Company policy question
        ↓
Retrieve authoritative enterprise knowledge
        ↓
Context
        ↓
LLM
```

```text
Live inventory question
        ↓
Database/API tool
        ↓
Current data
        ↓
LLM
```

```text
"If inventory is below threshold, create replenishment request"
        ↓
Agent/orchestrator
        ↓
Retrieve policy + query inventory
        ↓
Evaluate condition
        ↓
Authorized action tool
        ↓
Validate result
        ↓
LLM response
```

---

# 10. Canonical Enterprise AI Mental Model

This is the **canonical architecture diagram for the masterclass**. It is intentionally generic and contains no single business example.

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
                              │ • Request metadata           │
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
                    │ • Raw assistant messages                       │
                    │ • Timestamps                                   │
                    │ • Conversation metadata                        │
                    │ • Complete conversation record                 │
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
                              │ • Source authority           │
                              │ • Conversation continuity    │
                              │ • Information priority       │
                              │ • Token budget               │
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
                  │ to user            │       │ / external operation │
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

### Golden boundary

> **Router decides what capability/source is needed. Context Manager decides what information the LLM should see. Context Builder assembles that information into the model request. The LLM reasons and generates using the supplied context.**

# 11. Router / Orchestration — AI Engineer Scope

The **routing/orchestration layer is primarily an AI Engineer responsibility** in the application architecture.

The router decides what capability or information source is appropriate for a task. It does not have to be a giant hard-coded `if/else` tree; it can evolve from deterministic rules to model-based routing and eventually agentic orchestration.

### Exact pattern

```text
                         USER REQUEST
                              │
                              ▼
                    ┌───────────────────┐
                    │ AI APPLICATION    │
                    │ / ORCHESTRATOR    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ TASK / CONTEXT    │
                    │ DECISION LAYER    │
                    └─────────┬─────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
                RAG        Database      Tools/APIs
                 │            │            │
                 ▼            ▼            ▼
            Enterprise     Live data     Actions
             knowledge
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                     CONTEXT ENGINEERING
                              │
                         Token budget
                              │
                              ▼
                             LLM
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                  Answer              Action
```

### Examples

**General knowledge:**

```text
"What is an embedding?"
        ↓
General LLM knowledge
        ↓
LLM
```

**Enterprise policy:**

```text
"What is our inventory policy?"
        ↓
Router
        ↓
RAG / enterprise knowledge
        ↓
Retrieve + rank + context
        ↓
LLM
```

**Live enterprise data:**

```text
"What is inventory for plant 1001?"
        ↓
Router
        ↓
SQL/API tool
        ↓
Database
        ↓
LLM
```

**Action-oriented task:**

```text
"If plant 1001 is below threshold, create a replenishment request."
        ↓
Agent / orchestrator
        ↓
Retrieve business rule
        ↓
Query inventory
        ↓
Evaluate condition
        ↓
Call authorized action API
        ↓
Validate result
        ↓
LLM response
```

### Router evolution

#### V1 — Deterministic routing

```python
if requires_enterprise_policy(question):
    use_rag()
elif requires_live_data(question):
    use_database()
else:
    use_llm()
```

Useful for learning and simple stable workflows.

#### V2 — Model-based routing

```text
User request
    ↓
Router model / classifier
    ↓
Intent / task classification
    ↓
RAG / SQL / API / general LLM
```

#### V3 — Agentic orchestration

```text
User task
    ↓
Agent
    ↓
Reason / select capability
    ↓
Tool call
    ↓
Observe result
    ↓
Select next step
    ↓
Complete task
```

### Critical boundary

The **LLM provides language understanding, reasoning/generation, and can produce tool-call requests**. The application owns the actual routing policy, authorization, tool execution, enterprise-system integration, validation, and orchestration workflow.

The LLM should not be treated as the enterprise database or as the source of truth.

### Enterprise routing principle

> **Determine what the task requires → retrieve authoritative information or invoke an appropriate capability when needed → construct the best context → invoke the model → validate and/or safely execute the result.**

This is a core AI Engineer responsibility and will become central to our eventual enterprise agent.

# 12. RAG — Future Practical Module

## Core RAG pipeline

```text
Documents
   ↓
Parsing / ingestion
   ↓
Chunking
   ↓
Embedding model
   ↓
Vectors
   ↓
Vector database / index
   ↑
   │
User question
   ↓
Query embedding
   ↓
Vector search
   ↓
Candidate results
   ↓
Metadata filtering / reranking
   ↓
Relevant chunks
   ↓
Context builder
   ↓
Existing LLM
   ↓
Grounded answer + citations
```

RAG is a major context-engineering mechanism, not a replacement for context engineering itself.

Chunking, retrieval embeddings, vector storage/search, metadata filtering, reranking, retrieval evaluation, and context construction are primarily AI Engineer/RAG application responsibilities. The generation model remains an existing model component unless we choose to train/fine-tune one.

## RAG has two paths: Offline / Ingestion and Online / Query

RAG is best understood as two connected but different paths.

### 1. Offline / Ingestion path — prepare the knowledge

```text
Enterprise Data
(PDF / SharePoint / DB / etc.)
        │
        ▼
     Ingestion
        │
        ▼
     Parsing
        │
        ▼
    Chunking
        │
        ▼
    Metadata
        │
        ▼
   Embeddings
        │
        ▼
Vector / Search Index
```

**Purpose:** prepare enterprise knowledge so that it can be searched efficiently later.

The expensive preparation work — parsing, chunking, embedding, and indexing — should not be repeated for every user question. It is performed independently of individual queries and reused across many requests.

**Offline does not mean "run once."** The ingestion/indexing path can be batch, scheduled, incremental, or event-driven. When a document changes, the affected content can be re-ingested, re-processed, re-embedded, and re-indexed.

### 2. Online / Query path — retrieve knowledge for the current question

```text
User Question
      │
      ▼
Query Processing
      │
      ▼
Query Embedding
      │
      ▼
Search Index
      │
      ▼
Relevant chunks
      │
      ▼
Filter / Rank / Rerank
      │
      ▼
Context
      │
      ▼
LLM
      │
      ▼
Answer
```

**Purpose:** answer the current user request using the relevant knowledge that was prepared and indexed earlier.

### Why the separation matters

Without separation, every request could theoretically require:

```text
User question
      ↓
Read enterprise document
      ↓
Parse
      ↓
Chunk
      ↓
Embed
      ↓
Index
      ↓
Search
      ↓
Answer
```

That would be inefficient and would add unnecessary latency and compute cost.

The production pattern is therefore:

```text
              PREPARE KNOWLEDGE
                     │
                     ▼
               SEARCH INDEX
                     │
═════════════════════╪═════════════════════
                     │
               USER QUESTION
                     │
                     ▼
              RETRIEVE KNOWLEDGE
                     │
                     ▼
                    LLM
```

### Important mental model

> **Offline / ingestion prepares the searchable knowledge. Online / query retrieves the relevant knowledge for the current request.**

This separation is one of the first concepts to understand before learning query embeddings, vector similarity search, ranking, reranking, and advanced RAG.

---
                    RAG
                     │
                     ▼
              1. WHY RAG?
                     │
                     ▼
          2. RAG ARCHITECTURE
                     │
                     ▼
       ┌─────────────────────────┐
       │     INGESTION SIDE      │
       └────────────┬────────────┘
                    │
                    ▼
          3. Data Sources
             PDF / DOCX / HTML
             SharePoint / DB
             APIs / Files
                    │
                    ▼
          4. Ingestion
             Batch
             Incremental
             Event-driven
                    │
                    ▼
          5. Parsing / Extraction
             Text
             Tables
             Layout
             Metadata
                    │
                    ▼
          6. Cleaning / Normalization
                    │
                    ▼
          7. CHUNKING
             Fixed
             Recursive
             Semantic
             Parent-child
             Hierarchical
                    │
                    ▼
          8. Metadata
             ACL
             source
             page
             section
             version
             tenant
                    │
                    ▼
          9. EMBEDDINGS
             Text → Vector
                    │
                    ▼
         10. Embedding Models
             Hugging Face
             Sentence Transformers
             OpenAI
             BGE
             E5
             etc.
                    │
                    ▼
         11. Vector Storage
             FAISS
             pgvector
             Pinecone
             Milvus
             Weaviate
             Chroma
             Databricks Vector Search
                    │
                    ▼
         12. Vector Indexes
             HNSW
             IVF
             ANN
                    │
                    ▼
              SEARCH INDEX
                    │
════════════════════╪════════════════════
                    │
                    │ QUERY / ONLINE
                    │
                    ▼
             USER QUESTION
                    │
                    ▼
         13. Query Processing
                    │
                    ▼
         14. Query Embedding
                    │
                    ▼
         15. Retrieval
             Top-K
             similarity
             threshold
                    │
                    ▼
         16. Metadata Filtering
                    │
                    ▼
         17. Keyword Search
             BM25
                    │
                    ▼
         18. Hybrid Search
             Vector + Keyword
                    │
                    ▼
         19. Fusion
             RRF
             weighted fusion
                    │
                    ▼
         20. Ranking
                    │
                    ▼
         21. Reranking
             Cross Encoder
             BGE
             Cohere
                    │
                    ▼
         22. Context Selection
                    │
                    ▼
         23. Context Compression
                    │
                    ▼
         24. Prompt / Context Builder
                    │
                    ▼
                    LLM
                    │
                    ▼
             Grounded Answer
                    │
                    ▼
             Citations / Sources
                    │
════════════════════╪════════════════════
                    │
                    ▼
            ADVANCED RAG
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
 Query Rewrite   Multi Query    HyDE
        │           │            │
        └───────────┼────────────┘
                    ▼
           Parent-Child RAG
                    │
                    ▼
        Contextual Retrieval
                    │
                    ▼
          Multi-Hop Retrieval
                    │
                    ▼
              Graph RAG
                    │
                    ▼
             Agentic RAG
                    │
                    ▼
             Corrective RAG
                    │
                    ▼
          Adaptive / Self RAG
                    │
                    ▼
             RAG EVALUATION
                    │
        ┌───────────┼─────────────┐
        ▼           ▼             ▼
   Retrieval     Generation    End-to-End
   Evaluation    Evaluation    Evaluation
        │           │             │
        ▼           ▼             ▼
 Precision       Faithfulness   Answer quality
 Recall          Relevance      Groundedness
        │           │             │
        └───────────┼─────────────┘
                    ▼
             RAGAS / Custom
                    │
                    ▼
          PRODUCTION RAG
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
 Security       Performance     Cost
        │           │             │
        ▼           ▼             ▼
 ACL / RBAC     Latency        Token usage
 Multi-tenancy  Throughput      Caching
 Freshness      Scaling         Indexing
        │           │             │
        └───────────┼─────────────┘
                    ▼
             OBSERVABILITY
                    │
                    ▼
          LANGCHAIN / LLAMAINDEX
                    │
                    ▼
       ENTERPRISE RAG ARCHITECTURE
       
# 13. Roadmap

1. AI Fundamentals — started
2. LLM Fundamentals — started
3. Python LLM Application — completed first version
4. Conversation Context — completed first version
5. Token measurement — completed
6. Context Window / Token Budget — understood
7. Sliding-window Context Manager — completed baseline
8. Context compaction / summarization — completed experiment
9. Structured Memory — next
10. Semantic Retrieval
11. Embeddings
12. Vector Search
13. RAG + citations
14. RAG evaluation
15. Prompt/system instructions
16. Structured outputs
17. Tool calling
18. Router / orchestration
19. Agents
20. Agent memory
21. LangGraph / agent frameworks
22. Multi-agent systems
23. MCP
24. Evaluation and tracing
25. Security and guardrails
26. LLMOps / observability
27. Databricks AI / enterprise integration
28. Production deployment
29. Enterprise AI architecture
30. Capstone: production-style enterprise AI agent

## Current milestone

**Completed:** Python → Ollama → Llama 3.2, continuous chat, persistent conversation history, exact AI Engineer vs existing LLM boundary, token metrics, sliding-window context management, deliberate context failure, and LLM-generated summary/compaction experiment.

**New understanding:** Enterprise AI applications need a routing/orchestration layer that decides whether a task needs general LLM knowledge, enterprise retrieval, live database/API data, or an action/tool workflow. Enterprise sources remain the source of truth; LLM summaries and answers are derived information. Chat history, structured memory, RAG, and tools are distinct information/capability sources feeding relevance-aware context construction.

**Next:** Build Context Manager V1 against the persistent conversation store, then deliberately test its limitations before introducing historical retrieval, structured memory, embeddings, vector search, and RAG.
