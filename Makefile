.PHONY: all backend frontend install dev dev-backend dev-frontend build build-backend build-frontend up down logs clean lint lint-check format test test-backend test-frontend test-e2e pre-commit setup ci-check pre-push

# Colors
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m

# Default target
all: install dev

# Backend targets
backend:
	@echo "Backend directory: ./backend"

install-backend:
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	pip install black flake8 isort pytest-cov 2>/dev/null || true

dev-backend:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build-backend:
	cd backend && pip install -r requirements.txt

# Frontend targets
frontend:
	@echo "Frontend directory: ./frontend"

install-frontend:
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd frontend && npm ci

dev-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

# Combined targets
install: install-backend install-frontend

dev: dev-backend dev-frontend

build: build-backend build-frontend

# Docker Compose targets
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

build-images:
	docker compose build

rebuild:
	docker compose down && docker compose build --no-cache && docker compose up -d

# Development workflow
start-dev: up logs-backend

stop: down

# Code quality targets
lint:
	@echo "$(GREEN)Running backend linters...$(NC)"
	cd backend && black --check --line-length 100 app/ tests/ alembic/ 2>/dev/null || (echo "Install black: pip install black" && exit 1)
	cd backend && isort --check-only app/ tests/ alembic/ 2>/dev/null || (echo "Install isort: pip install isort" && exit 1)
	cd backend && flake8 --config .flake8 .
	@echo "$(GREEN)Running frontend linter...$(NC)"
	cd frontend && npm run lint
	@echo "$(GREEN)All linting passed!$(NC)"

lint-check:
	@echo "$(YELLOW)Running lint checks (without formatting)...$(NC)"
	@cd backend && black --check --line-length 100 app/ tests/ alembic/ 2>/dev/null || (echo "Install black: pip install black" && exit 1)
	@cd backend && isort --check-only app/ tests/ alembic/ 2>/dev/null || (echo "Install isort: pip install isort" && exit 1)
	@cd backend && flake8 --config .flake8 .
	@cd frontend && npm run lint
	@echo "$(GREEN)All lint checks passed!$(NC)"

format:
	@echo "$(GREEN)Formatting backend code...$(NC)"
	cd backend && black --line-length 100 app/ tests/ alembic/
	cd backend && isort app/ tests/ alembic/
	@echo "$(GREEN)Backend code formatted!$(NC)"

# Testing targets
test:
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd frontend && npm run test -- --run

test-backend:
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd frontend && npm run test -- --run

test-e2e:
	@echo "$(GREEN)Running E2E tests...$(NC)"
	cd frontend && npm run build
	cd frontend && npm run test:e2e -- --project=chromium --reporter=list

# Pre-commit setup
pre-commit:
	@echo "$(GREEN)Installing pre-commit...$(NC)"
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg

setup: pre-commit
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

# CI check - run this before pushing!
ci-check: lint build test test-e2e
	@echo ""
	@echo "✅ All checks passed! Ready to push."

# Pre-push hook - run this automatically before git push
pre-push:
	@echo "🔍 Running full pre-push validation..."
	@echo ""
	@echo "📦 Checking backend..."
	@cd backend && black --line-length 100 app/ tests/ alembic/
	@cd backend && isort --check-only app/ tests/ alembic/
	@cd backend && flake8 --config .flake8 .
	@cd backend && PYTHONPATH=. python -m pytest tests/ -v --tb=short
	@echo ""
	@echo "🎨 Checking frontend..."
	@cd frontend && npm run lint
	@cd frontend && npm run build
	@cd frontend && npm run test -- --run
	@echo ""
	@echo "✅ All pre-push checks passed! Ready to push."

# Cleanup
clean:
	@echo "$(GREEN)Cleaning up...$(NC)"
	docker compose down -v 2>/dev/null || true
	rm -rf backend/*.db backend/__pycache__ backend/.pytest_cache 2>/dev/null || true
	rm -rf frontend/node_modules frontend/dist frontend/test-results frontend/playwright-report 2>/dev/null || true
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Database
db-init:
	cd backend && python -m alembic upgrade head

db-migrate:
	cd backend && python -m alembic revision --autogenerate -m "Auto migration"

db-upgrade:
	cd backend && python -m alembic upgrade head

db-seed:
	cd backend && python -m scripts.init_db

db-backup:
	cd backend && python -m scripts.backup_db backup

db-restore:
	cd backend && python -m scripts.backup_db restore $(BACKUP_FILE)

db-list-backups:
	cd backend && python -m scripts.backup_db list

db-cleanup-backups:
	cd backend && python -m scripts.backup_db cleanup

# Help
help:
	@echo "InfraMon Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Start development servers"
	@echo "  make build        - Build all containers"
	@echo "  make up           - Start containers with Docker Compose"
	@echo "  make down         - Stop containers"
	@echo ""
	@echo "Before Pushing:"
	@echo "  make ci-check     - Run all CI checks (lint + build + tests + e2e)"
	@echo "  make pre-push     - Same as ci-check (used by git hook)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"
	@echo "  make test-e2e     - Run E2E tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run all linters"
	@echo "  make lint-check   - Check linting (no changes)"
	@echo "  make format       - Format code automatically"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make setup        - Install pre-commit hooks"
