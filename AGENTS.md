# InfraMon Development Guidelines

This document provides guidelines and commands for agents working on the InfraMon codebase.

## Project Overview

InfraMon is a Docker container monitoring system with:
- **Frontend**: React 18 + TypeScript + Tailwind CSS 4
- **Backend**: Python 3.11 + FastAPI + SQLite + Alembic
- **Testing**: pytest (backend) + Vitest (frontend) + Playwright (E2E)

## Build Commands

### Installation

```bash
make install              # Install all dependencies (backend + frontend)
make install-backend     # Install backend dependencies only
make install-frontend   # Install frontend dependencies only
```

### Development Servers

```bash
make dev                 # Start both backend and frontend dev servers
make dev-backend         # Start backend (uvicorn with reload)
make dev-frontend        # Start frontend (Vite HMR)
```

### Docker Operations

```bash
make up                  # Start containers with Docker Compose
make down                # Stop containers
make logs                # View logs
make logs-backend        # View backend logs
make logs-frontend       # View frontend logs
make rebuild             # Rebuild and restart containers
```

### Building for Production

```bash
make build              # Build all containers
make build-backend      # Build backend container
make build-frontend     # Build frontend container
```

### Database Commands

```bash
make db-init            # Initialize database with Alembic
make db-migrate         # Generate new migration
make db-upgrade         # Apply migrations
make db-seed            # Seed database with initial data
make db-backup          # Create database backup
make db-restore         # Restore from backup
```

## Linting and Formatting

### Run All Linters

```bash
make lint               # Run backend + frontend linters (auto-format)
make lint-check         # Check linting without making changes
make format             # Format backend code only
```

### Backend Linting

Backend uses: Black (100 char line length), isort, flake8

```bash
# Check formatting
cd backend && ./venv/bin/black --check --line-length 100 app/ tests/ alembic/

# Auto-format
cd backend && ./venv/bin/black --line-length 100 app/ tests/ alembic/
cd backend && ./venv/bin/isort app/ tests/ alembic/

# Run flake8
cd backend && ./venv/bin/flake8 --config .flake8 .
```

### Frontend Linting

Frontend uses: ESLint + TypeScript ESLint

```bash
cd frontend && npm run lint
```

### Pre-commit Hooks

```bash
make setup              # Install pre-commit hooks
make pre-commit        # Run pre-commit manually
```

Hooks run: trailing-whitespace, end-of-file-fixer, black, isort, flake8, eslint

## Testing

### Run All Tests

```bash
make test              # Backend + frontend tests
```

### Backend Tests (pytest)

```bash
# Run all backend tests
make test-backend
cd backend && PYTHONPATH=$(pwd) ./venv/bin/pytest tests/ -v

# Run single test file
cd backend && ./venv/bin/pytest tests/unit/test_api_containers.py -v

# Run single test function
cd backend && ./venv/bin/pytest tests/unit/test_api_containers.py::test_list_containers -v

# Run by keyword
cd backend && ./venv/bin/pytest -k "containers" -v

# Run with coverage
cd backend && ./venv/bin/pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
cd backend && ./venv/bin/pytest --cov=app --cov-report=html
```

### Frontend Tests (Vitest)

```bash
# Run all frontend tests
make test-frontend
cd frontend && npm test

# Run single test file
cd frontend && npm test -- src/components/ContainerCard.test.tsx

# Run in watch mode
cd frontend && npm test -- --watch

# Run with coverage
cd frontend && npm test -- --coverage
```

### E2E Tests (Playwright)

```bash
# Run E2E tests
make test-e2e
cd frontend && npm run build && npm run test:e2e -- --project=chromium

# Run with UI
cd frontend && npm run test:e2e:ui

# Run headed
cd frontend && npm run test:e2e:headed

# Show report
cd frontend && npm run test:e2e:report
```

### CI Check

```bash
make ci-check           # Run lint + build + test + e2e
make pre-push          # Same as ci-check (used by git hook)
```

## Code Style Guidelines

### Python (Backend)

**Line Length**: 100 characters

**Imports**: Use isort with Black profile
```python
# Standard library
import asyncio
from pathlib import Path

# Third party
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from app.api.v1.router import api_router
from app.core.config import settings
```

**Naming Conventions**:
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Prefixed with `_` for private/internal members

**Type Hints**: Required for function signatures
```python
from typing import List, Optional

async def get_container(container_id: str) -> Optional[Container]:
    ...
```

**Error Handling**:
```python
try:
    result = await operation()
except SpecificException as e:
    logger.error(f"Context: {e}")
    raise HTTPException(status_code=400, detail="User-friendly message")
```

**Async/Await**: Use throughout for I/O operations

**Docstrings**: Google style for public functions
```python
def func(arg1: str, arg2: int) -> bool:
    """Short summary.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        SpecificError: When this error occurs
    """
```

**File Structure** (app/):
```
app/
├── api/v1/       # API routes
├── core/         # Config, security, logging
├── db/           # Database, models, schemas
├── services/     # Business logic
└── main.py       # FastAPI app entry
```

### TypeScript/React (Frontend)

**TypeScript**: Strict mode enabled

**Naming**:
- `camelCase` for variables, functions, props
- `PascalCase` for components, types, interfaces
- `SCREAMING_SNAKE_CASE` for constants

**Component Structure**:
```tsx
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Container, ContainerStats } from '@/types'
import { ContainerCard } from '@/components/ContainerCard'

interface Props {
  containers: Container[]
  onSelect: (id: string) => void
}

export function ContainersPage({ containers, onSelect }: Props) {
  const [filter, setFilter] = useState('')

  const filtered = containers.filter(c =>
    c.name.toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div className="p-4">
      <FilterInput value={filter} onChange={setFilter} />
      <div className="grid gap-4">
        {filtered.map(c => (
          <ContainerCard key={c.id} container={c} onSelect={onSelect} />
        ))}
      </div>
    </div>
  )
}
```

**Imports**:
- React imports first
- External libraries
- Internal components/hooks/types
- Use `@/` alias for src/ imports

**State Management**:
- React Query for server state
- Zustand for client state
- Local state (useState/useReducer) for UI state

**Styling**: Tailwind CSS with `clsx` for conditional classes

**Error Handling**:
```tsx
try {
  await queryClient.fetchQuery({ queryKey: ['containers'] })
} catch (error) {
  console.error('Failed to fetch:', error)
  toast.error('Unable to load containers')
}
```

**Testing**: React Testing Library for components, mock external dependencies

**File Structure** (src/):
```
src/
├── components/    # Reusable UI components
├── hooks/         # Custom React hooks
├── pages/         # Page components
├── services/      # API client (axios)
├── types/         # TypeScript types
└── test/          # Test utilities
```

## Configuration Files

- **Backend**: `backend/pyproject.toml` (Black, isort, pytest, coverage)
- **Backend**: `backend/.flake8` (Flake8 settings)
- **Frontend**: `frontend/.eslintrc.json` (ESLint)
- **Frontend**: `frontend/tsconfig.json` (TypeScript)
- **Both**: `.pre-commit-config.yaml` (Pre-commit hooks)

## Common Patterns

### Backend API Pattern
```python
# Router: app/api/v1/endpoints/containers.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.container import ContainerService
from app.api.deps import get_current_user

router = APIRouter(prefix="/containers", tags=["containers"])

@router.get("/{container_id}")
async def get_container(
    container_id: str,
    service: ContainerService = Depends(get_container_service),
    user = Depends(get_current_user)
) -> ContainerResponse:
    container = await service.get(container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    return container
```

### Frontend API Call Pattern
```typescript
// Service: src/services/api.ts
import axios from 'axios'
import type { Container } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

export const containersApi = {
  list: () => api.get<Container[]>('/api/v1/containers'),
  get: (id: string) => api.get<Container>(`/api/v1/containers/${id}`),
  start: (id: string) => api.post(`/api/v1/containers/${id}/start`),
  // ...
}
```

### React Query Pattern
```typescript
export function useContainers() {
  return useQuery({
    queryKey: ['containers'],
    queryFn: () => containersApi.list().then(r => r.data),
    refetchInterval: 5000, // Auto-refresh
  })
}
```

## Before Submitting

1. Run `make pre-push` to validate all changes
2. Ensure all tests pass
3. Verify linting passes
4. Check coverage remains above the threshold
5. Ensure no sensitive data in commits

## Git Commit Rules

### Never Skip Verification
- **NEVER use `--no-verify` or `--no-hooks`** to bypass pre-commit or pre-push hooks
- **ALWAYS** let hooks run their full validation
- If hooks fail, fix the issues rather than bypassing them

### Always Stage All Relevant Files
- **NEVER** skip files from a commit intentionally
- Stage all files that are part of the feature/fix
- Use `git add -A` or stage files individually for clarity
- Review `git status` before committing to ensure nothing is unintentionally left out

### Commit Message Requirements
- Write clear, descriptive commit messages
- Include context about what changed and why
- Reference issue numbers if applicable

### Pre-commit Hook Fixes
If pre-commit hooks auto-modify files (black, isort, end-of-file-fixer):
1. Let the hooks make their changes
2. Stage the modified files: `git add <files>`
3. Amend the commit: `git commit --amend --no-edit`
4. Never skip hooks to avoid auto-formatting issues

### Proper Commit Workflow
```bash
# 1. Check status
git status

# 2. Stage all relevant files
git add -A  # or git add <specific-files>

# 3. Review changes
git diff --cached

# 4. Commit
git commit -m "Clear commit message"

# 5. If hooks modify files, amend
git add <modified-files>
git commit --amend --no-edit

# 6. Push
git push origin <branch>
```

### Never Do This
- ❌ `git commit --no-verify`
- ❌ `git push --no-verify`
- ❌ Skipping files from commit intentionally
- ❌ Bypassing pre-push hooks
