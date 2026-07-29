# API Documentation

## Health
- `GET /health` - System health status
- `GET /health/ready` - Readiness check

## Documents
- `POST /documents/index` - Index documents
- `GET /documents/` - List all documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

## Chat
- `POST /chat/` - Send message
- `GET /chat/{id}` - Get conversation
- `DELETE /chat/{id}` - Delete conversation

## Search
- `POST /search/` - Semantic search
