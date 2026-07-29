# Python Code Snippets

## List Comprehension
```python
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

## Dictionary Operations
```python
user = {"name": "Alice", "age": 30}
user["email"] = "alice@example.com"
for key, value in user.items():
    print(f"{key}: {value}")
```

## File I/O
```python
with open("data.txt", "r") as f:
    content = f.read()

with open("output.txt", "w") as f:
    f.write("Hello")
```
