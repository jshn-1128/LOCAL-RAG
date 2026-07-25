# Local RAG

A production-ready, privacy-first Retrieval-Augmented Generation system that runs entirely on local infrastructure. Uses Ollama for LLM inference and local embedding models — no data ever leaves your machine.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     User Interface                   │
│                  (CLI / API / Web UI)                │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  Orchestration Layer                  │
│           (Document Ingestion, Query Processing)      │
└────────────────────────┬────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────┐            ┌─────────▼────────┐
│  Vector Store    │            │    LLM Engine     │
│  (ChromaDB /     │            │    (Ollama)       │
│   FAISS)         │            │                   │
└────────┬────────┘            └─────────┬─────────┘
         │                               │
┌────────▼────────┐            ┌─────────▼────────┐
│   Embedding     │            │   Local Models    │
│   Model         │            │   (Llama 3,       │
│                  │            │    Mistral, etc.)  │
└─────────────────┘            └──────────────────┘
```

## Planned Features

- [ ] Local LLM inference via Ollama
- [ ] Document ingestion (PDF, TXT, Markdown)
- [ ] Text chunking and embedding
- [ ] Vector store indexing and retrieval
- [ ] RAG query pipeline with context augmentation
- [ ] CLI interface
- [ ] REST API
- [ ] Web UI (Streamlit)
- [ ] Multi-user support
- [ ] Document management dashboard

## Project Status

**Phase 1 — Project Initialization** ✅

Current phase focus: project scaffolding, configuration management, and environment setup.

## Folder Structure

```
local-rag/
├── app/          # Application source code
├── configs/      # Configuration files
├── data/         # Data directory (documents, vector store)
├── docs/         # Documentation
├── logs/         # Application logs
├── models/       # Local model files
├── scripts/      # Utility scripts
├── tests/        # Test suite
├── .venv/        # Python virtual environment
├── .env.example  # Environment variables template
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## License

Distributed under the MIT License. See `LICENSE` for more information.
