#!/usr/bin/env bash
set -euo pipefail

echo "=== Local RAG — Bootstrap ==="
echo ""

# Verify pyenv
if ! command -v pyenv &>/dev/null; then
    echo "ERROR: pyenv not found."
    echo "Install it: brew install pyenv"
    echo "Then: pyenv install 3.11.9 && pyenv local 3.11.9"
    exit 1
fi

# Verify pyenv has 3.11.x active
PYTHON_VERSION=$(pyenv version-name 2>/dev/null || echo "none")
if [[ "$PYTHON_VERSION" != 3.11.* ]]; then
    echo "ERROR: Python $PYTHON_VERSION is active, but 3.11.x is required."
    echo "Run: pyenv install 3.11.9 && pyenv local 3.11.9"
    echo "Then re-run this script."
    exit 1
fi

echo "  pyenv: $PYTHON_VERSION ✅"

# Locate the Python interpreter pyenv manages
PYTHON=$(pyenv which python 2>/dev/null || echo "")
if [ -z "$PYTHON" ]; then
    echo "ERROR: pyenv cannot resolve a Python interpreter."
    exit 1
fi

echo "  Interpreter: $PYTHON"
$PYTHON --version

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv
    echo "  ✅ .venv created"
else
    echo ""
    echo "  ✅ .venv already exists"
fi

# Activate and install
echo ""
echo "Installing dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip setuptools wheel --quiet
pip install -e ".[dev]" --quiet
echo "  ✅ Dependencies installed"

# Install pre-commit hooks
echo ""
echo "Installing pre-commit hooks..."
pre-commit install 2>/dev/null
echo "  ✅ Pre-commit hooks installed"

# Summary
echo ""
echo "=== Bootstrap complete ==="
echo ""
echo "  pyenv:      $PYTHON_VERSION ✅"
echo "  .venv:      created ✅"
echo "  packages:   installed ✅"
echo "  pre-commit: installed ✅"
echo ""
echo "  Next: source .venv/bin/activate"
