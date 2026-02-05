.PHONY: all backend frontend install dev dev-backend dev-frontend build build-backend build-frontend up down logs clean lint test

# Default target
all: install dev

# Backend targets
backend:
	@echo "Backend directory: ./backend"

install-backend:
	cd backend && pip install -r requirements.txt

dev-backend:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build-backend:
	cd backend && pip install -r requirements.txt

# Frontend targets
frontend:
	@echo "Frontend directory: ./frontend"

install-frontend:
	cd frontend && npm install

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

# Testing targets
test:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing
	cd frontend && npm run test

test-backend:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && npm run test

# Code quality targets
lint:
	cd backend && black app/ tests/ && isort app/ tests/ && flake8 app/ tests/
	cd frontend && npm run lint

lint-backend:
	cd backend && black app/ tests/ && isort app/ tests/ && flake8 app/ tests/

lint-frontend:
	cd frontend && npm run lint

# Cleanup
clean:
	docker compose down -v
	rm -rf backend/*.db backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

# Database
db-init:
	cd backend && alembic upgrade head

db-migrate:
	cd backend && alembic revision --autogenerate -m "Auto migration"

db-upgrade:
	cd backend && alembic upgrade head

# Help
help:
	@echo "Available targets:"
	@echo "  all          - Install dependencies and start development (default)"
	@echo "  install      - Install all dependencies"
	@echo "  dev          - Start development servers (backend + frontend)"
	@echo "  dev-backend  - Start backend development server"
	@echo "  dev-frontend - Start frontend development server"
	@echo "  build        - Build all containers for production"
	@echo "  up           - Start containers with Docker Compose"
	@echo "  down         - Stop containers"
	@echo "  logs         - Show all container logs"
	@echo "  clean        - Clean up containers and build artifacts"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run code formatters and linters"
	@echo "  help         - Show this help message"
