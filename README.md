# Review Summary Platform

AI-powered review summary and analysis platform that aggregates user reviews, generates intelligent summaries using AI, and provides actionable analytics.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Features

- **AI-Powered Summaries** - Automatically generate concise summaries from multiple reviews using OpenAI or Gemini
- **Review Analytics** - Visual dashboards with rating distributions, sentiment trends, and keyword analysis
- **User Authentication** - Secure login and registration via Supabase Auth
- **Server-Side Rendering** - Fast, SEO-friendly pages with Jinja2 templates
- **REST API** - Full-featured API with OpenAPI documentation
- **Docker Ready** - One-command deployment with Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Supabase project (free tier works)
- OpenAI or Gemini API key

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/min1336/review_summary.git
cd review_summary
```

2. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your Supabase and AI API credentials
```

3. **Start with Docker Compose**

```bash
docker-compose up --build
```

4. **Access the application**

- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload
```

## API Documentation

Interactive API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server is running.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reviews` | List reviews with pagination |
| POST | `/api/v1/reviews` | Create a new review |
| GET | `/api/v1/reviews/{id}` | Get review by ID |
| POST | `/api/v1/summaries/generate` | Generate AI summary |
| GET | `/api/v1/analytics/dashboard` | Get analytics data |

## Project Structure

```
review_summary/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Configuration, security, exceptions
│   ├── dto/                 # Pydantic request/response schemas
│   ├── models/              # Domain entities
│   ├── services/            # Business logic layer
│   ├── repositories/        # Data access layer (Supabase)
│   ├── api/v1/              # REST API routers
│   ├── pages/               # Server-rendered page routers
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JavaScript assets
├── tests/
│   ├── unit/                # Unit tests with mocked dependencies
│   └── integration/         # Integration tests with TestClient
├── docker/                  # Docker configuration files
├── scripts/                 # Utility scripts
├── supabase/                # Supabase migrations and config
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## Development Guide

### Architecture

The project follows a **Layered Architecture**:

```
Presentation (Routers) -> Application (Services) -> Infrastructure (Repositories)
```

- **Routers** handle HTTP requests and responses
- **Services** contain business logic
- **Repositories** manage data access via Supabase

### Code Quality

```bash
# Linting
ruff check app/ --fix
ruff format app/

# Type checking
mypy app/ --ignore-missing-imports
```

### Git Workflow

1. Create a feature branch from `main`: `git checkout -b feature/your-feature`
2. Make changes following the coding conventions in `CLAUDE.md`
3. Write tests for your changes
4. Ensure all checks pass
5. Create a Pull Request

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

### Testing Strategy

- **Unit tests**: Mock external dependencies (Supabase, AI APIs)
- **Integration tests**: Use FastAPI TestClient for endpoint testing
- **Coverage target**: 80% minimum

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding conventions defined in `CLAUDE.md`
4. Write tests for your changes
5. Ensure all tests pass and linting is clean
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run pre-commit checks
ruff check app/ --fix
ruff format app/
mypy app/ --ignore-missing-imports
pytest tests/ -v
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
