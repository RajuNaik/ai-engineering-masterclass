$handbook = "MASTER_AI_ENGINEER_HANDBOOK.md"

$section = @'

# RAG Practical Build — Ingestion Foundation Checkpoint

We have now started the hands-on RAG implementation. The first objective is to build the **ingestion side** before moving into parsing, chunking, embeddings, vector search, retrieval, reranking, and advanced RAG.

## RAG ingestion architecture — current stage

```text
SOURCE
  │
  ▼
INGESTION CONNECTOR
  │
  ▼
MICROSOFT ENTRA ID
  │
  ▼
RBAC AUTHORIZATION
  │
  ▼
AZURE ADLS GEN2 — RAW LAYER
  │
  └── rag-raw/
       ├── files/
       │   ├── pdf/
       │   ├── docx/
       │   ├── pptx/
       │   ├── xlsx/
       │   ├── txt/
       │   └── images/
       │
       ├── github/
       ├── datasets/
       ├── apis/
       └── web/
```

The Raw layer stores source data **as received**, before RAG-specific processing. We deliberately do not place chunks, embeddings, or vectors in this layer.

## Why ADLS Gen2 is our Raw layer

For this lab, Azure Data Lake Storage Gen2 is the durable landing zone for source material. The storage account uses **Hierarchical Namespace (HNS)** so that we can use ADLS Gen2 filesystem/directory semantics.

```text
Python application
      │
      ▼
DefaultAzureCredential
      │
      ▼
Microsoft Entra ID
      │
      ▼
RBAC
      │
      ▼
ADLS Gen2
      │
      ▼
rag-raw/
```

We use Microsoft Entra authentication rather than embedding storage keys or SAS tokens in the Python application.

## VS Code / Python / Azure CLI — roles

These are complementary, not competing technologies:

```text
VS Code
  └── Development environment

Python
  └── Our application / ingestion logic

Azure SDK
  └── Python → Azure programmatic access

Azure CLI
  └── Administration, diagnostics, authentication checks,
      and infrastructure/data-plane verification

Azure Portal
  └── Visual administration and inspection
```

The production-style ingestion application is **Python + Azure SDK + Microsoft Entra authentication**. Azure CLI is useful for setup and troubleshooting; it is not the RAG ingestion engine itself.

## First source completed — local file

We created a realistic enterprise-style test document:

```text
rag_test_policy.txt
```

The Python connector uploads it into:

```text
rag-raw/files/
```

Completed flow:

```text
Local document
      │
      ▼
Python ingestion connector
      │
      ▼
DefaultAzureCredential
      │
      ▼
Microsoft Entra ID
      │
      ▼
RBAC
      │
      ▼
ADLS Gen2
      │
      ▼
rag-raw/files/
      │
      ▼
rag_test_policy.txt
```

### What this proves

- Azure Storage account is available.
- Hierarchical Namespace is enabled.
- ADLS Gen2 access works.
- The `rag-raw` filesystem/container exists.
- Microsoft Entra authentication works.
- RBAC authorization works.
- Python can connect through the Azure SDK.
- Python can create/access an ADLS directory.
- Python can upload a source document into the Raw layer.

## Important Raw-layer principle

The Raw layer is **not** the RAG knowledge index.

```text
RAW
 │
 │ source preservation
 ▼
PARSING
 │
 ▼
CLEANING / NORMALIZATION
 │
 ▼
CHUNKING
 │
 ▼
EMBEDDING
 │
 ▼
VECTOR / SEARCH INDEX
```

We will keep these stages separate so that the original source remains available and downstream processing can be repeated without reacquiring the source.

## Source types planned for ingestion

The Raw layer is being prepared for multiple common RAG source categories:

```text
1. Local / document files       → rag-raw/files/
2. GitHub repositories          → rag-raw/github/
3. Public datasets              → rag-raw/datasets/
4. APIs / REST sources          → rag-raw/apis/
5. Web sources                  → rag-raw/web/
```

These are **source categories**, not the complete RAG architecture. Each connector will eventually normalize its output into a common ingestion contract.

## Current RAG implementation boundary

We are intentionally stopping here for this learning checkpoint.

### Completed

```text
Source identification
       ↓
Azure Raw-layer setup
       ↓
ADLS Gen2
       ↓
Entra + RBAC
       ↓
Python → ADLS
       ↓
Local-file ingestion
```

### Not started yet

```text
Parsing
Cleaning
Document structure extraction
Chunking
Chunk strategies
Metadata enrichment
Embedding models
Vector databases
Vector indexes
Query embeddings
Similarity search
Hybrid search
Reranking
Context compression
RAG evaluation
Advanced RAG
```

## Next step

Before building the GitHub connector, establish a **common ingestion contract** so every source connector follows the same enterprise pattern for:

- source identity
- document identity
- source type
- destination path
- ingestion timestamp
- checksum / duplicate detection
- version information
- metadata
- ingestion status
- error handling
- idempotency

Then implement **Source #2 — GitHub**.

> **Checkpoint:** We have successfully built and tested the first source → Python ingestion → ADLS Gen2 Raw flow. Tomorrow we resume from the common ingestion contract and continue source-by-source before moving deeper into RAG processing.
'@

Add-Content -Path $handbook -Value $section -Encoding UTF8
Write-Host "RAG ingestion section appended to $handbook"
