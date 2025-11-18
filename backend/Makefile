# ChirpNeighbors Backend Makefile
# Quick commands for development and testing

.PHONY: help install test test-unit test-integration test-coverage lint format clean

help:  ## Show this help message
	@echo "ChirpNeighbors Backend - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

test:  ## Run all tests
	pytest -v

test-unit:  ## Run unit tests only
	pytest -v -m "not integration"

test-integration:  ## Run integration tests only
	pytest -v -m integration

test-coverage:  ## Run tests with coverage report
	pytest -v --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

test-watch:  ## Run tests in watch mode (re-run on file changes)
	pytest-watch -v

lint:  ## Run linting checks
	ruff check app/
	mypy app/ --ignore-missing-imports

format:  ## Format code with ruff
	ruff format app/
	ruff check --fix app/

format-check:  ## Check code formatting without making changes
	ruff format --check app/

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml

run:  ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:  ## Run production server
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

db-migrate:  ## Run database migrations
	alembic upgrade head

db-downgrade:  ## Rollback last database migration
	alembic downgrade -1

db-reset:  ## Reset database (WARNING: deletes all data)
	alembic downgrade base
	alembic upgrade head

docker-build:  ## Build Docker image
	docker build -t chirpneighbors-backend:latest .

docker-run:  ## Run Docker container
	docker-compose up -d

docker-stop:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## Show Docker logs
	docker-compose logs -f backend

shell:  ## Open Python shell with app context
	python -i -c "from app.main import app; from app.db import *"

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

security-check:  ## Run security checks
	bandit -r app/ -ll
	safety check

deps-update:  ## Update dependencies
	pip-compile requirements.in
	pip-compile requirements-dev.in

.DEFAULT_GOAL := help
