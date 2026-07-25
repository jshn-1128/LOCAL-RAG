#!/usr/bin/env bash
set -euo pipefail

echo "=== Local RAG — Bootstrap ==="
echo ""

# Verify Python version
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found. Install Python 3.11 via pyenv."
    exit 1
fi

PYTHON_VERSION=$($PYTHON --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [ "$PYTHON_VERSION" != "3.11" ]; then
    echo "WARNING: Expected Python 3.11, got $PYTHON_VERSION"
    echo "Use pyenv: pyenv local 3.11.9"
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv
    echo "  ✅ .venv created"
else
    echo "  ✅ .venv already exists"
fi

# Activate and install
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

echo ""
echo "=== Bootstrap complete ==="
echo "Activate: source .venv/bin/activate"
