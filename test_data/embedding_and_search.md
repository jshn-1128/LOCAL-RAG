# Embeddings and Semantic Search

Embeddings are numerical representations of text that capture semantic meaning. They are the foundation of modern search and RAG systems.

## What are Embeddings?

An embedding is a dense vector of floating-point numbers where semantically similar texts map to nearby points in the vector space. The distance between vectors correlates with semantic similarity.

### Properties of Good Embeddings

- **Semantic similarity**: Similar meanings → close vectors
- **Fixed dimensionality**: All embeddings have the same length
- **Dense representation**: Most dimensions are non-zero

## Embedding Models

### Sentence Transformers

The `sentence-transformers` library provides easy-to-use embedding models:
- **all-MiniLM-L6-v2**: 384 dimensions, fast, good general purpose
- **all-mpnet-base-v2**: 768 dimensions, higher quality, slower
- **BAAI/bge-base-en-v1.5**: 768 dimensions, state-of-the-art

### OpenAI Embeddings
- text-embedding-3-small: 1536 dimensions
- text-embedding-3-large: 3072 dimensions

## Similarity Metrics

### Cosine Similarity
```
cosine_similarity(A, B) = A·B / (|A| × |B|)
```
Range: [-1, 1]. 1 = identical direction, 0 = orthogonal, -1 = opposite.

### Euclidean Distance (L2)
```
euclidean(A, B) = sqrt(sum((A_i - B_i)²))
```
Smaller values = more similar.

### Dot Product
```
dot(A, B) = sum(A_i × B_i)
```
Used when embeddings are normalized.

## Semantic Search Pipeline

```
Indexing:
Documents → Chunk → Embed → Store in Vector DB

Search:
Query → Embed → Vector DB Search → Ranked Results
```

## Chunking for Search

Good chunking is critical for search quality:
- **Too small**: Missing context
- **Too large**: Diluted relevance
- **Overlap**: Preserves boundary context

## Vector Search Algorithms

### Exact Search (Brute Force)
Compare query against all vectors. O(n) per query. OK for small collections.

### Approximate Nearest Neighbor (ANN)
Trade accuracy for speed. Common algorithms:
- **HNSW** (Hierarchical Navigable Small World): Graph-based
- **IVF** (Inverted File Index): Cluster-based
- **PQ** (Product Quantization): Compression-based

### ChromaDB Default
ChromaDB uses HNSW by default, which balances search speed and accuracy well for collections up to millions of vectors.

## Relevance vs Ranking

Search quality depends on:
1. **Retrieval recall**: Are relevant documents found?
2. **Ranking precision**: Are irrelevant documents filtered out?
3. **Chunk quality**: Are chunks self-contained and meaningful?
