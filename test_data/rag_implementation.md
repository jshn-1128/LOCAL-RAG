# Implementing a RAG System

This document describes a practical implementation of a RAG system using Python.

## Architecture Overview

The system uses a clean hexagonal architecture with the following layers:

### Core Components

1. **Document Loaders** — Load documents from various formats (PDF, DOCX, TXT, Markdown)
2. **Chunkers** — Split documents into manageable pieces (RecursiveChunker, SemanticChunker)
3. **Embeddings** — Convert text chunks to vectors using sentence-transformers
4. **Vector Store** — ChromaDB stores embeddings and enables similarity search
5. **Retrieval Service** — Finds relevant chunks given a query
6. **Prompt Builder** — Constructs prompts with context for the LLM
7. **Chat Service** — Manages conversations with history
8. **Memory** — SQLite-based conversation memory

### Data Flow

```
Document → Loader → Chunker → Embedder → Vector DB
                                            ↓
User Query → Embedder → Vector DB → Retriever → Prompt Builder → LLM → Answer
```

## Chunking Configuration

Recommended settings for production:
- Chunk size: 512 tokens
- Chunk overlap: 64 tokens
- Chunking strategy: RecursiveChunker for general use

## Embedding Configuration

Default model: all-MiniLM-L6-v2
- Embedding dimensions: 384
- Dimensionality: appropriate for semantic search
- Speed: ~10ms per batch of 100 texts

## Retrieval Configuration

- Top-K: 4 chunks by default
- Similarity metric: cosine similarity (default in ChromaDB)
- Cosine similarity range: [-1, 1], values closer to 1 indicate higher similarity

## LLM Integration

The system connects to Ollama running locally:
- API: http://localhost:11434
- Default model: llama3.2 (configurable)
- Supports streaming responses

## Prompt Template

```
You are a helpful assistant with access to retrieved context.
---
Context:
{context}
---
Conversation History:
{history}
---
Question: {question}
---
Answer the question based on the provided context. If the context
does not contain enough information, say so.
```
