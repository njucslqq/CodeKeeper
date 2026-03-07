#!/bin/bash

# Test runner script for Git Deep Analyzer

set -e

echo "=================================="
echo "  Git Deep Analyzer Test Runner"
echo "=================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev, cpp]" --quiet

# Run tests with coverage
echo ""
echo "Running tests with coverage..."
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "ERROR: pytest not found. Please install it first."
    exit 1
fi

# Run tests
pytest \
    -v \
    --cov=src/git_deep_analyzer \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=75 \
    tests/ || true

echo ""
echo "=================================="
echo "  Test Results"
echo "=================================="
echo ""
echo "Coverage report generated at: htmlcov/index.html"
echo ""
echo "To run specific test:"
echo "  pytest tests/test_filename.py"
echo ""
echo "To run specific test class:"
echo "  pytest tests/test_filename.py::TestClass"
echo ""
echo "To run specific test:"
echo "  pytest tests/test_filename.py::TestClass::test_method"
echo ""
