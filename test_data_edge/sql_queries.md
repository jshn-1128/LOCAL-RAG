# SQL Query Examples

## SELECT
```sql
SELECT * FROM users WHERE active = 1;
SELECT name, email FROM users ORDER BY created_at DESC;
SELECT COUNT(*) FROM orders GROUP BY status;
```

## JOIN
```sql
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.total > 100;
```

## INSERT
```sql
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com');
```

## CREATE TABLE
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```
