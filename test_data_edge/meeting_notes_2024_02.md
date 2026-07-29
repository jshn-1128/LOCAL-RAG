# Meeting Notes - Feb 20, 2024

**Attendees**: Alice, Bob, Charlie, Dave
**Topic**: RAG Implementation Review

## Discussion
- Alice presented RAG architecture
- ChromaDB selected as vector store
- All-MiniLM-L6-v2 chosen for embeddings
- Target: Local deployment with Ollama

## Decisions
- Use gemma3:1b for initial deployment
- Python 3.11+ required
- FastAPI for backend API
