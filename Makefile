.PHONY: install lint format typecheck test check clean

install:
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format . --check

format-fix:
	ruff format .

typecheck:
	mypy .

test:
	pytest

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html

check: lint format typecheck test

clean:
	rm -rf .venv build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

precommit-install:
	pre-commit install

precommit-run:
	pre-commit run --all-files
