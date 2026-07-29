# Database Systems

Databases are organized collections of structured information or data, typically stored electronically in a computer system.

## Types of Databases

### Relational Databases (SQL)
Store data in tables with predefined schemas. Data is related through foreign keys.

Popular relational databases:
- **PostgreSQL**: Advanced open-source RDBMS with ACID compliance
- **MySQL**: Widely used open-source RDBMS
- **SQLite**: Embedded, serverless database engine
- **MariaDB**: Fork of MySQL

### NoSQL Databases
Designed for specific data models not fitting the relational model.

Types of NoSQL databases:
- **Document stores**: MongoDB, CouchDB — store JSON-like documents
- **Key-value stores**: Redis, DynamoDB — simple key-value pairs
- **Column-family stores**: Cassandra, HBase — columns instead of rows
- **Graph databases**: Neo4j — for connected data

## SQL Basics

```sql
-- Create table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE
);

-- Insert data
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Query data
SELECT * FROM users WHERE name LIKE 'A%';

-- Join tables
SELECT orders.id, users.name
FROM orders
JOIN users ON orders.user_id = users.id;
```

## ACID Properties

- **Atomicity**: Transactions are all-or-nothing
- **Consistency**: Data must be valid according to rules
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data survives failures

## Indexing

Indexes speed up data retrieval at the cost of slower writes. Common index types include B-tree, Hash, and GiST indexes.

## Vector Databases

Vector databases like ChromaDB, Pinecone, and Weaviate store embeddings for similarity search. They use algorithms like HNSW (Hierarchical Navigable Small World) for approximate nearest neighbor search. These are essential for RAG applications.

## Database Comparison

| Feature | PostgreSQL | MongoDB | Redis |
|---------|-----------|---------|-------|
| Type | Relational | Document | Key-Value |
| Schema | Fixed | Flexible | Flexible |
| Query Lang | SQL | MQL | Commands |
| ACID | Yes | Yes (v4.0+) | Partial |
| Use Case | Complex queries | Rapid prototyping | Caching |
