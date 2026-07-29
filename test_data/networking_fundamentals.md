# Networking Fundamentals

Computer networking connects devices to share data and resources. Networks range from small local networks to the global internet.

## OSI Model

The OSI (Open Systems Interconnection) model has 7 layers:

| Layer | Name | Example Protocols |
|-------|------|------------------|
| 7 | Application | HTTP, FTP, SMTP |
| 6 | Presentation | SSL/TLS |
| 5 | Session | NetBIOS, RPC |
| 4 | Transport | TCP, UDP |
| 3 | Network | IP, ICMP |
| 2 | Data Link | Ethernet, Wi-Fi |
| 1 | Physical | Cables, radio |

## TCP/IP Model

The TCP/IP model has 4 layers:
1. **Application** (HTTP, FTP, DNS)
2. **Transport** (TCP, UDP)
3. **Internet** (IP)
4. **Network Access** (Ethernet)

### TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| Connection | Connection-oriented | Connectionless |
| Reliability | Guaranteed delivery | Best-effort |
| Ordering | Preserved | Not guaranteed |
| Speed | Slower | Faster |
| Use cases | Web, email, file transfer | Streaming, DNS, gaming |

## HTTP Protocol

HTTP (Hypertext Transfer Protocol) is the foundation of web communication.

### HTTP Methods
- **GET**: Retrieve resource
- **POST**: Create resource
- **PUT**: Update/replace resource
- **PATCH**: Partial update
- **DELETE**: Remove resource

### HTTP Status Codes
- **1xx**: Informational
- **2xx**: Success (200 OK, 201 Created)
- **3xx**: Redirection (301 Moved, 304 Not Modified)
- **4xx**: Client Error (400 Bad Request, 404 Not Found)
- **5xx**: Server Error (500 Internal Server Error)

## REST API Design

REST (Representational State Transfer) is an architectural style for designing networked applications. Key principles:
- Resources identified by URLs
- Standard HTTP methods for operations
- Stateless communication
- JSON or XML for data representation

## API Rate Limiting

Rate limiting controls traffic to APIs. Common strategies:
- Token bucket
- Leaky bucket
- Fixed window
- Sliding window

## DNS

The Domain Name System translates domain names (example.com) to IP addresses. It's a hierarchical, distributed database.
