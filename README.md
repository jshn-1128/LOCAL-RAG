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
**Phase 2 — Development Standards** ✅
**Phase 3 — Application Architecture** ✅
**Phase 4 — Configuration & Logging** ✅

Current phase focus: implementing application features.

## Configuration System

Configuration is managed through a single `Settings` class using Pydantic Settings v2. All settings are:

- **Typed** — every field has a Python type
- **Validated** — cross-field rules enforced at construction
- **Immutable** — frozen after creation, no runtime mutation
- **Environment-aware** — `development` vs `production` modes
- **Docker-ready** — all values overridable via `LOCAL_RAG_*` env vars

### Environment Variables

All environment variables use the `LOCAL_RAG_` prefix. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `LOCAL_RAG_ENVIRONMENT` | `development` | Runtime environment (`development` or `production`) |
| `LOCAL_RAG_LOG_LEVEL` | `INFO` | Root log level |
| `LOCAL_RAG_API_HOST` | `0.0.0.0` | FastAPI bind address |
| `LOCAL_RAG_API_PORT` | `8000` | FastAPI port |
| `LOCAL_RAG_LLM_HOST` | `http://localhost:11434` | Ollama server URL |
| `LOCAL_RAG_LLM_MODEL` | `llama3.2` | Default LLM model |
| `LOCAL_RAG_LLM_TEMPERATURE` | `0.7` | LLM temperature (0.0–2.0) |
| `LOCAL_RAG_LLM_MAX_TOKENS` | `2048` | Maximum generated tokens |
| `LOCAL_RAG_TOP_K` | `4` | Retrieved chunks per query |
| `LOCAL_RAG_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model name |
| `LOCAL_RAG_EMBEDDING_DIMENSIONS` | `384` | Embedding vector size |
| `LOCAL_RAG_CHUNK_SIZE` | `512` | Document chunk size (characters) |
| `LOCAL_RAG_CHUNK_OVERLAP` | `64` | Chunk overlap (must not exceed chunk_size) |
| `LOCAL_RAG_MEMORY_MAX_HISTORY` | `20` | Max conversation turns retained |

### Adding New Settings

1. Add the field to `app/config/settings.py` with a type, default, and validation.
2. Update `.env.example` if the setting should be user-configurable.
3. If the value is an engineering constant (not user-configurable), add it to `app/config/constants.py`.
4. Inject `Settings` into your service via the constructor (never import `Settings()` directly).

### Configuration Flow

```
.env / environment vars
       │
       ▼
Settings()  ← instantiated ONCE in app.py lifespan
       │
       ├──► injected into RAGPipelineFactory
       │         └──► passed to each service constructor
       │
       └──► stored in app.state for API dependency injection
```

## Logging System

Logging is centrally configured in `app/config/logging.py` and initialized during application startup.

### Logger Hierarchy

Loggers follow the Python package structure using `logging.getLogger(__name__)`:

```
local_rag                    (root — level from config)
├── local_rag.api            (FastAPI middleware, routes)
├── local_rag.application    (services)
├── local_rag.config         (config loading)
├── local_rag.domain         (domain events)
├── local_rag.infrastructure (adapters)
└── local_rag.pipeline       (composition root)
```

### Handlers

- **Console**: Writes to stdout. Level = `DEBUG` in development, `INFO` in production.
- **Rotating File**: Writes to `logs/local-rag.log`. Level = `INFO`. Max 10 MB per file, 5 backups.

### Log Format

```
2024-01-15 10:30:45,123 | INFO     | app.config.settings | Configuration loaded
```

### Using Loggers in Your Code

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Document processed: %s", doc_id)
```

### Third-Party Logging

The following libraries are set to `WARNING` level to reduce noise:
- `httpx`
- `urllib3`
- `chromadb`

## Development Setup

### Prerequisites

- Python 3.11.9 (managed via pyenv)
- [pyenv](https://github.com/pyenv/pyenv) (recommended)
- [Ollama](https://ollama.ai) (required for LLM features)

### Quick Start

```bash
# Clone and enter the repository
git clone <repo-url>
cd local-rag

# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env
```

Or use the bootstrap script:

```bash
./scripts/bootstrap.sh
source .venv/bin/activate
```

### Code Formatting

```bash
make format        # Check formatting
make format-fix    # Auto-fix formatting
```

Ruff handles both linting and formatting. Configuration is in `pyproject.toml`.

### Linting

```bash
make lint
```

Ruff replaces Flake8, isort, and pyupgrade with a single fast tool.

### Type Checking

```bash
make typecheck
```

MyPy runs with strict mode. Configuration is in `pyproject.toml`.

### Testing

```bash
make test        # Run tests with coverage
make coverage    # Run tests with HTML coverage report
```

Pytest is configured in `pyproject.toml` with coverage enabled by default.

### Pre-commit

```bash
make precommit-run  # Run all hooks manually
```

Pre-commit runs automatically on `git commit`. Hooks include Black, Ruff, YAML/TOML validation, and security checks.

### Full Check

```bash
make check  # Runs lint → format check → typecheck → test
```

## Folder Structure

```
local-rag/
├── app/                # Application source code
├── configs/            # Configuration files
├── data/               # Data directory (documents, vector store)
├── docs/               # Documentation
├── logs/               # Application logs
├── models/             # Local model files
├── scripts/            # Utility scripts
├── tests/              # Test suite
├── .github/            # GitHub templates and CI
├── .vscode/            # Editor configuration
├── .editorconfig       # Cross-editor settings
├── .env.example        # Environment variables template
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── LICENSE
├── Makefile
├── pyproject.toml
└── README.md
```

## License

Distributed under the MIT License. See `LICENSE` for more information.
