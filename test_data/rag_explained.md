# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is an AI framework that combines information retrieval with text generation. It enhances LLM outputs by retrieving relevant information from external knowledge sources before generating a response.

## How RAG Works

### The RAG Pipeline

1. **Ingestion Phase**
   - Documents are loaded
   - Text is split into chunks
   - Each chunk is embedded into a vector
   - Vectors are stored in a vector database

2. **Retrieval Phase**
   - User query is embedded into a vector
   - Similar chunks are retrieved from the vector database
   - Retrieved chunks form the context

3. **Generation Phase**
   - System prompt defines the AI's behavior
   - Retrieved context is injected into the prompt
   - LLM generates answer grounded in the context

### RAG Architecture

```
User Query → Embed → Vector DB → Retrieve Context
                                       ↓
System Prompt + Context + Query → LLM → Answer
```

## Why RAG?

- **Grounding**: Reduces hallucinations by providing factual context
- **Up-to-date**: Knowledge can be updated without retraining
- **Transparency**: Sources can be attributed
- **Cost-effective**: Smaller models can answer domain-specific questions

## RAG vs Fine-tuning

| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| Knowledge updates | Instant (re-index) | Requires retraining |
| Cost | Low (no training) | High (GPU hours) |
| Transparency | High (source attribution) | Low (black box) |
| Domain depth | Retrieval-dependent | Can learn patterns |
| Hallucination risk | Lower (grounded) | Higher |

## Vector Databases

Popular vector databases for RAG include ChromaDB, Pinecone, Weaviate, and Qdrant. They store embeddings and enable similarity search using metrics like cosine similarity or Euclidean distance.

## Chunking Strategies

- **Fixed-size chunking**: Split at character/token count
- **Semantic chunking**: Split at topic boundaries
- **Recursive chunking**: Hierarchical splitting with overlap

## Embedding Models

Embeddings convert text to numerical vectors. Common models include all-MiniLM-L6-v2 (384 dimensions), OpenAI text-embedding-ada-002 (1536 dimensions), and BERT-based models.
