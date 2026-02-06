# Makefile for NEZHA-RED

.PHONY: install run test lint format typecheck clean

# Install dependencies
install:
	pip install -r requirements.txt

# Run the main GUI demo
run:
	python -m demos

# Run all tests
test:
	pytest

# Run single test file
run-test:
	pytest tests/test_puzzle.py

# Run with coverage
coverage:
	pytest --cov=src --cov-report=term-missing

# Linting
lint:
	flake8 src/ tests/

# Auto-format code
format:
	black src/ tests/ demos/

# Type checking
typecheck:
	mypy src/

# Check all (run before commits)
check: format lint typecheck test

# Clean generated files
clean:
	rm -rf demos/output/*.mid demos/output/*.txt
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Help
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Launch GUI game"
	@echo "  make test       - Run all tests"
	@echo "  make run-test   - Run single test file example"
	@echo "  make coverage   - Run tests with coverage"
	@echo "  make lint       - Run flake8 linting"
	@echo "  make format     - Auto-format with black"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make check      - Run format, lint, typecheck, and test"
	@echo "  make clean      - Clean generated files"
