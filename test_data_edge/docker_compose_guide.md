# Docker Compose Guide

Docker Compose defines multi-container Docker applications.

## Basic docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
  redis:
    image: redis:alpine
```

## Common Commands
- `docker compose up` - Start services
- `docker compose down` - Stop services
- `docker compose logs` - View logs

Docker Compose uses YAML files to configure application services.
