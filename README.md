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

Current phase focus: project scaffolding, configuration management, and environment setup.

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
