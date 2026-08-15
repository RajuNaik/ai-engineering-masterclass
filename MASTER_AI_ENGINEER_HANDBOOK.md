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
                    │                         │
                    │ RAG                     │
                    │ Tools / APIs            │
                    │ Agent orchestration     │
                    │ Memory                  │
                    │ Guardrails              │
                    │ Evaluation              │
                    │ Security                │
                    │ Observability           │
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
- Agent orchestration
- Agent memory
- Guardrails
- Evaluation
- Observability/tracing
- Security/authorization integration
- Cost and latency controls
- Deployment and production operations

### Ownership table

| Component | Primary scope |
|---|---|
| Tokenizer used by model | Existing model/runtime |
| Token IDs | Existing model/runtime |
| Transformer | Existing LLM |
| Attention | Existing LLM |
| Trained weights | Existing model |
| Next-token generation | Existing LLM |
| Model inference | Runtime/platform |
| Prompt construction | AI Engineer |
| Context selection | AI Engineer |
| Conversation state | AI Engineer |
| RAG | AI Engineer |
| Chunking | AI Engineer |
| Retrieval embeddings | AI Engineer / RAG pipeline |
| Vector search | AI Engineer / data platform |
| Tool integration | AI Engineer |
| Agent orchestration | AI Engineer |
| Memory | AI Engineer |
| Evaluation | AI Engineer |
| Security/authorization | AI Engineer + security/platform |
| Observability | AI Engineer + platform |
| Deployment | AI Engineer + platform/DevOps |

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
- Per-request LLM input/output token metrics from the Ollama response

## Current conversation state

```python
messages = []
```

User and assistant messages are appended to the list and the conversation is sent to the model on each turn.

### Where is it stored?

Currently **only in RAM of the running Python process**.

There is:
- No database
- No persistent file
- No long-term memory store
- No history after the process exits

This is session context, not persistent memory.

### Why send history again?

The application effectively sends:

```text
previous conversation
+
new user question
→
LLM
```

The model is not independently remembering our application session; our application provides the relevant history in the request.

# 6. Tokens — Practical Measurement

A **token** is a unit used by the model's tokenizer to represent text. A token is not necessarily equal to one word; tokenization depends on the model/tokenizer and can split words, punctuation, whitespace patterns, or other text into multiple pieces.

For our current application, we do not manually convert the messages into token IDs. Instead, Ollama's inference stack processes the request and returns useful token-count metrics.

Our application now exposes:

```text
Messages in application memory
Input tokens for this request
Output tokens generated
```

Conceptually:

```text
Python messages[]
        │
        ▼
Context sent for this request
        │
        ▼
Model runtime / tokenizer
        │
        ├── input tokens  ← prompt/context size
        │
        ▼
       LLM
        │
        ├── output tokens ← generated response size
        │
        ▼
     response
```

### Important distinction

```text
Application message count ≠ token count
```

For example:

```text
7 messages
```

does **not** mean 7 tokens. A single message can contain hundreds or thousands of tokens.

### Why AI Engineers care about token counts

Even though tokenization is handled by the model/runtime, token counts matter for:

- Context-window limits
- Latency
- Cost for hosted models
- Prompt/context optimization
- RAG retrieval budgets
- Conversation compaction
- Model selection
- Production capacity planning

# 7. Context Window and Token Budget — Next Concept

The next problem we will demonstrate is that conversation history can grow much faster in tokens than the simple message count suggests.

```text
More conversation
       ↓
More input tokens
       ↓
Larger context
       ↓
Higher latency / cost
       ↓
Eventually context constraints
```

The AI Engineer's job is not to manually tokenize every request, but to **engineer the context sent to the model within an intentional token budget**.

Production strategies can include:
- Keep recent messages
- Summarize older history
- Retrieve relevant memory
- Retrieve only relevant RAG chunks
- Compress context
- Enforce maximum context budgets
- Route requests to an appropriate model

# 8. Enterprise Reality Checkpoint — Conversation Context

Our learning implementation:

```text
messages[]
   ↓
Python RAM
   ↓
entire conversation
   ↓
LLM
```

A production system may use:

```text
Conversation
 ↓
Application state
 ↓
Persistent store
 ↓
Context selection / retrieval
 ↓
Model
```

Production concerns include:
- Context-window limits
- Token usage/cost
- Latency
- Relevance of old history
- Summarization/compaction
- Privacy and retention
- Access control
- Auditability

A production context builder may combine recent chat, summarized history, relevant memory, RAG results, tool results, and business rules rather than blindly sending the entire conversation.

# 9. RAG — Future Practical Module

Core RAG pipeline:

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
Relevant chunks
   ↓
Context builder
   ↓
Existing LLM
   ↓
Grounded answer + citations
```

Chunking, retrieval embeddings, vector storage/search, metadata filtering, reranking, retrieval evaluation, and context construction are primarily part of the **AI Engineer/RAG application side**. The generation model remains an existing model component unless we choose to train/fine-tune one.

# 10. Roadmap

1. AI Fundamentals — started
2. LLM Fundamentals — started
3. Python LLM Application — completed first version
4. Conversation Context — completed first version
5. Token measurement — completed first practical instrumentation
6. Tokens and Context Windows — **current**
7. Context Management / Context Engineering
8. Embeddings
9. Vector Search
10. RAG + citations
11. RAG evaluation
12. Prompt/system instructions
13. Structured outputs
14. Tool calling
15. Agents
16. Agent memory
17. LangGraph / agent frameworks
18. Multi-agent systems
19. MCP
20. Evaluation and tracing
21. Security and guardrails
22. LLMOps / observability
23. Databricks AI / enterprise integration
24. Production deployment
25. Enterprise AI architecture
26. Capstone: production-style enterprise AI agent

## Current milestone

**Completed:** Python → Ollama → Llama 3.2, continuous chat, in-memory conversation context, exact AI Engineer vs existing LLM boundary, and practical token metrics.

**Current:** tokens and context windows.

**Next:** context-window pressure → token budget → context management.
