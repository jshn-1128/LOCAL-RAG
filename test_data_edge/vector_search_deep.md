# Vector Search Deep Dive

## How Vector Search Works

1. Text is converted to embeddings (vectors of floats)
2. Similar vectors are close in vector space
3. Search finds nearest neighbors

## Similarity Metrics

### Cosine Similarity
```
cosine_sim(A, B) = A·B / (|A| × |B|)
```
Range: [-1, 1]. Default in ChromaDB.

### Euclidean Distance
```
euclidean(A, B) = sqrt(sum((A_i - B_i)²))
```
Smaller = more similar.

## ANN Algorithms
- HNSW: Graph-based, good balance
- IVF: Cluster-based, fast indexing
- PQ: Compression, memory efficient

ChromaDB uses HNSW by default.
