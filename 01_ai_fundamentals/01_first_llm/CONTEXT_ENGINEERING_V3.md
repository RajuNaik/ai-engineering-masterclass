# Context Engineering — V3: Summarization and Compaction

## Why V2 failed

Our sliding-window context manager kept only the most recent 3 turns. That reduced context size, but it also removed older information. We demonstrated the failure when the model misunderstood **RAG** after the original RAG discussion fell outside the recent-message window.

```text
Full session
    |
    v
Sliding window
    |
    +--> lower token usage
    |
    +--> older information lost
```

Core principle:

> Recency is not the same as relevance.

## V3 goal

Preserve important information from older conversation while still limiting raw context.

```text
Full conversation
       |
       +----------------------+
       |                      |
       v                      v
 Older history          Recent turns
       |                      |
       v                      |
 Conversation summary         |
       |                      |
       +----------+-----------+
                  |
                  v
            Context Builder
                  |
                  v
                 LLM
```

## Implementation

The application now maintains:

```python
messages = []
conversation_summary = ""
```

The model context contains:

1. System instructions
2. Rolling conversation summary, when available
3. Most recent N turns

Current baseline:

```text
Recent turns retained = 3
Older information     = rolling summary
```

## Why this is better than a pure sliding window

V2:

```text
Old context -> discarded
```

V3:

```text
Old context
    |
    v
Summarize important information
    |
    v
Compact representation
    |
    v
Keep recent raw turns
```

This allows the system to retain important facts, decisions, requirements, terminology, and references without sending the entire raw transcript.

## Important trade-off

Summarization is **lossy**. The summary model can omit details, misunderstand statements, merge facts, or lose exact wording. Production systems should therefore distinguish between conversational summaries and authoritative/durable memory or source data.

## Cost and latency trade-off

Compaction itself requires an LLM call in our implementation.

```text
No compaction
    -> larger context every request

With compaction
    -> extra summarization calls
    -> smaller subsequent contexts
```

The engineering problem becomes an optimization between context size, summarization frequency, latency, cost, information retention, and answer quality.

## Enterprise pattern

```text
                    SESSION STATE
                         |
             +-----------+-----------+
             |                       |
             v                       v
        Recent turns          Older information
             |                       |
             |                 +-----+------+
             |                 |            |
             |                 v            v
             |             Summary       Durable
             |             memory        memory
             |                 |            |
             +-----------------+------------+
                               |
                               v
                      Context Manager
                               |
                     relevance + budget
                               |
                               v
                              LLM
```

## What comes next

V3 is still not the final solution. Next improvements will include structured memory, semantic retrieval of older conversation, RAG, token-budget-aware context selection, and evaluation of context quality.

The eventual goal is not:

> Send as much history as possible.

It is:

> **Construct the smallest sufficient context that gives the model the information it needs for the current task.**
