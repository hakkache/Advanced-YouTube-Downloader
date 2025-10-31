# Makefile for Advanced YouTube Downloader

.PHONY: help install install-dev test lint format clean run setup check-deps security

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  setup       - Set up development environment"
	@echo "  run         - Run the Streamlit application"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting (flake8)"
	@echo "  format      - Format code (black)"
	@echo "  security    - Run security checks (bandit, safety)"
	@echo "  check-deps  - Check for dependency issues"
	@echo "  clean       - Clean up temporary files"
	@echo "  help        - Show this help message"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 bandit safety pip-tools

setup: install-dev
	@echo "Setting up development environment..."
	@echo "Creating downloads directory..."
	@mkdir -p downloads
	@echo "Development environment ready!"

# Run the application
run:
	streamlit run app.py

# Testing
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=app --cov=scheduler_service --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 . --exclude=venv,__pycache__,.git --max-line-length=100

format:
	black . --exclude="venv|__pycache__|.git|downloads"

format-check:
	black --check --diff . --exclude="venv|__pycache__|.git|downloads"

# Security
security:
	bandit -r . -f json -o bandit-report.json --exclude ./venv,./downloads,./test_downloads,./__pycache__ || true
	safety check --json --output safety-report.json || true
	@echo "Security reports generated: bandit-report.json, safety-report.json"

# Dependency management
check-deps:
	pip list --outdated
	pip check

update-deps:
	pip-compile --upgrade requirements.in
	pip install -r requirements.txt

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.coverage" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -f bandit-report.json safety-report.json

# Development workflow
dev-setup: setup
	@echo "Installing pre-commit hooks..."
	@pip install pre-commit || echo "pre-commit not available, skipping hooks"
	@pre-commit install || echo "Could not install pre-commit hooks"

# Check everything before committing
check-all: format-check lint test security
	@echo "All checks passed! Ready to commit."

# Quick development cycle
dev-test: format lint test
	@echo "Development tests completed."