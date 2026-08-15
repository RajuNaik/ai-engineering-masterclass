# RAG Ingestion — Current Learning Checkpoint

> Hands-on checkpoint for the Master AI Engineer RAG module. We are intentionally stopping after the Raw/ADLS ingestion layer before parsing, cleaning, chunking, embeddings, or vector search.

## Current Architecture

```text
                         ENTERPRISE / PUBLIC SOURCES
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
       Local Documents            GitHub                  Public APIs
       PDF / DOCX / TXT             │                        │
             │                      │                        │
             └──────────────────────┼────────────────────────┘
                                    ▼
                         PYTHON INGESTION APP
                                    │
                                    ▼
                         Microsoft Entra ID
                                    │
                                    ▼
                                  RBAC
                                    │
                                    ▼
                              Azure ADLS Gen2
                                    │
                                    ▼
                               rag-raw/
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
       files/                    github/                  datasets/
          │
          ├── pdf/
          ├── docx/
          ├── pptx/
          ├── xlsx/
          ├── txt/
          └── images/
                                    │
                                    ▼
                             Later: Processing
                                    │
                       Parsing → Cleaning → Chunking
                                    │
                             Embeddings → Search
```

## What We Completed

### Azure foundation

- Azure Storage Account created for the RAG lab.
- Hierarchical Namespace enabled, making it an ADLS Gen2 account.
- `rag-raw` created as a private filesystem/container.
- Microsoft Entra authentication configured.
- `Storage Blob Data Contributor` assigned to the development identity.
- Azure CLI installed for local-development authentication.
- `az login` successfully authenticated against the correct tenant/subscription.
- ADLS access verified through `--auth-mode login`.

### First ingestion path

```text
Local file
    ↓
Python ingestion script
    ↓
DefaultAzureCredential
    ↓
Microsoft Entra ID
    ↓
RBAC
    ↓
ADLS Gen2
    ↓
rag-raw/files/
    ↓
rag_test_policy.txt
```

The first enterprise-style test document, `rag_test_policy.txt`, was successfully uploaded to ADLS Gen2.

### Raw-zone structure

```text
rag-raw/
├── files/
│   ├── pdf/
│   ├── docx/
│   ├── pptx/
│   ├── xlsx/
│   ├── txt/
│   └── images/
├── github/
├── datasets/
├── apis/
└── web/
```

These directories represent source/ingestion categories. They are not processing stages.

## Important Architecture Decisions

### Python is the ingestion engine

VS Code is our development environment. Python is the actual ingestion application. Azure CLI is only a local authentication/administration tool; it is not the ingestion engine.

```text
VS Code
  ↓
Python application
  ↓
Azure SDK
  ↓
DefaultAzureCredential
  ↓
Microsoft Entra ID
  ↓
ADLS Gen2
```

The same Python application can later run in Azure with Managed Identity while continuing to use `DefaultAzureCredential`.

### Raw layer principle

The Raw layer preserves source artifacts before RAG-specific transformations.

```text
SOURCE → RAW
        ≈ preserve

RAW → PARSED
      transform

PARSED → CHUNKS
         split

CHUNKS → EMBEDDINGS
         represent

EMBEDDINGS → SEARCH INDEX
             searchable
```

We have deliberately not introduced parsing, OCR, cleaning, chunking, embeddings, vector databases, reranking, or RAG frameworks yet.

## Next Step

Before adding more connectors, design a **common ingestion contract** so every source connector produces consistent metadata and writes through a common ADLS Raw writer.

Then implement source connectors in this order:

1. Local files — completed first proof of concept
2. GitHub public repositories
3. Public/API sources
4. Hugging Face/public datasets
5. Web/Wikipedia/Common Crawl

After the ingestion layer is complete, move to:

```text
ADLS Raw
   ↓
Parsing / Extraction
   ↓
Cleaning / Normalization
   ↓
Chunking
   ↓
Metadata enrichment
   ↓
Embeddings
   ↓
Vector / Search Index
```

## Current Stop Point

**RAG ingestion is the active module. We are stopping here for this session.**

The next session starts with the **common ingestion contract and GitHub connector**. Do not jump to chunking or embeddings until the major source ingestion patterns are understood and implemented.
