# CLAUDE.md - Review Summary Platform

## Project Overview
AI-powered review summary and analysis platform built with Python/FastAPI + Supabase.

## Tech Stack
- Python 3.12+ with strict type hints
- FastAPI + Jinja2 SSR
- Pydantic v2 for DTOs
- Supabase (PostgreSQL + Auth)
- Docker + Docker Compose
- pytest for testing

## Architecture
Layered Architecture with strict dependency rules:
- Presentation (Routers) -> Application (Services) -> Infrastructure (Repositories)
- Upper layers depend on lower layers only
- Never import routers from services

## Coding Conventions

### Python Style
- Use ruff for linting and formatting (line-length: 100)
- Use mypy strict mode for type checking
- All functions must have type hints (parameters and return types)
- Use `from __future__ import annotations` where needed

### Naming
- Files: snake_case (review_service.py)
- Classes: PascalCase (ReviewService)
- Functions/methods: snake_case (create_review)
- Constants: UPPER_SNAKE_CASE

### Clean Code
- Functions should be 20 lines or fewer
- Single Responsibility Principle
- Meaningful variable and function names
- Docstrings for all public functions

## Project Structure
```
app/
├── main.py          # FastAPI entry point
├── core/            # Config, security, exceptions
├── dto/             # Pydantic request/response schemas
├── models/          # Domain entities
├── services/        # Business logic
├── repositories/    # Data access (Supabase)
├── api/v1/          # REST API routers
├── pages/           # Jinja2 page routers
├── templates/       # HTML templates
└── static/          # CSS, JS
tests/
├── unit/            # Unit tests (mock dependencies)
└── integration/     # Integration tests (TestClient)
```

## Development Rules

### Git Workflow
- NEVER commit directly to main
- Always create feature branches: feature/*, fix/*, test/*
- Write descriptive commit messages
- PRs require CI passing before merge

### TDD Approach
1. Write test first
2. Implement minimum code to pass
3. Refactor

### Testing
- Run: `pytest tests/ -v --cov=app`
- Unit tests: mock external dependencies (Supabase, AI APIs)
- Integration tests: use FastAPI TestClient
- Target: 80% code coverage

### Linting & Type Check
- `ruff check app/`
- `ruff format app/`
- `mypy app/ --ignore-missing-imports`

## Common Commands
```bash
# Development
uvicorn app.main:app --reload

# Testing
pytest tests/ -v --cov=app --cov-report=term-missing

# Linting
ruff check app/ --fix
ruff format app/

# Type checking
mypy app/ --ignore-missing-imports

# Docker
docker-compose up --build
```

## Important Notes
- Environment variables are managed via .env (see .env.example)
- Supabase client is created per-request via dependency injection
- AI service supports both OpenAI and Gemini APIs
- All API responses follow consistent error format: {"error": str, "detail": any}
