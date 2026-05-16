.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies with Poetry
	poetry install

dev: ## Run development server
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests with pytest
	poetry run pytest -v --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	poetry run ptw --runner "pytest -v"

lint: ## Run linting with ruff
	poetry run ruff check app/ tests/

format: ## Format code with black and ruff
	poetry run black app/ tests/
	poetry run ruff check --fix app/ tests/

type-check: ## Run type checking with mypy
	poetry run mypy app/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf dist/ build/

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f backend

docker-shell: ## Open shell in backend container
	docker-compose exec backend /bin/bash

migrate-create: ## Create a new migration
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate-up: ## Run migrations
	poetry run alembic upgrade head

migrate-down: ## Rollback last migration
	poetry run alembic downgrade -1

migrate-history: ## Show migration history
	poetry run alembic history --verbose

db-reset: ## Reset database (drop and recreate)
	poetry run alembic downgrade base
	poetry run alembic upgrade head

seed-db: ## Seed database with sample data
	poetry run python scripts/seed_db.py

all: format lint type-check test ## Run all checks
