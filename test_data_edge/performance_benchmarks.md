# Performance Benchmarks

## RAG Pipeline Latency

| Stage | Average | P95 |
|-------|---------|-----|
| Embedding | 50ms | 150ms |
| Vector Search | 10ms | 30ms |
| Prompt Construction | 1ms | 2ms |
| LLM Generation | 1.2s | 3s |
| Total | 1.3s | 3.2s |

## Memory Usage
- Embedding Model: ~400MB
- Ollama (1B model): ~800MB on disk
- ChromaDB: ~2MB for 100 docs
- Application: ~50MB

## Scaling
- 100 documents: <1s index time
- 1000 documents: ~5s index time
- 10000 documents: ~60s index time
