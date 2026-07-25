.PHONY: install format format-fix lint typecheck test coverage check clean precommit-install precommit-run

install:
	pip install -e ".[dev]"

format:
	ruff format . --check

format-fix:
	ruff format .

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html

check: lint format typecheck test

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

precommit-install:
	pre-commit install

precommit-run:
	pre-commit run --all-files
