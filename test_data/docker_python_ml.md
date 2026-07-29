# Docker for Python ML Projects

Using Docker to containerize machine learning and data science Python applications.

## Why Docker for ML?

- **Reproducibility**: Same environment everywhere
- **Dependency management**: Isolated dependencies via containers
- **Deployment**: Easy deployment to cloud or edge
- **Scaling**: Container orchestration with Kubernetes

## Dockerfile for ML Applications

```dockerfile
FROM python:3.11-slim

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

## Docker Compose for RAG Applications

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
    environment:
      - LOCAL_RAG_LLM_HOST=http://ollama:11434
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  ollama_data:
```

## GPU Support in Docker

For ML workloads, NVIDIA GPU support requires:
1. NVIDIA Container Toolkit installed
2. `--gpus all` flag or Docker Compose device reservations
3. CUDA-compatible base image

## Best Practices

### Image Size Optimization
- Use slim Python images
- Multi-stage builds for compilation
- Clean apt cache after installs
- Use `--no-cache-dir` for pip

### Security
- Don't run as root
- Use read-only filesystems where possible
- Scan images for vulnerabilities
- Pin dependency versions

## Performance Considerations

- Volume mounts for model weights (avoid copying large files)
- Shared memory for multiprocessing (`--shm-size=8g`)
- Resource limits for memory and CPU
- Health checks for service readiness

## Testing Docker Images

```bash
# Build
docker build -t rag-app:latest .

# Test locally
docker run --rm -p 8000:8000 rag-app:latest

# Check logs
docker logs <container-id>
```
