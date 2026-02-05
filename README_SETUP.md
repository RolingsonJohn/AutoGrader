# AutoGrader 2.0 - Setup & Usage Guide

## Overview

AutoGrader 2.0 is a comprehensive automated code grading system featuring:
- ✅ Dual architecture (Django + FastAPI)
- ✅ RAG-powered code evaluation
- ✅ LLM integration (Ollama, Groq, Google Generative AI)
- ✅ 9 improvement categories with 40+ features
- ✅ Comprehensive test suite
- ✅ Production-ready with CI/CD

## Quick Start

### 1. Clone and Install

```bash
cd AutoGrader
pip install -r requirements.txt
pip install -e ".[dev]"  # For development
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env and add your credentials
```

Required environment variables:
```env
DJANGO_SECRET_KEY=your-secret-key
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
FASTAPI_PORT=8001
API_KEY_GROQ=your-groq-key  # Optional
API_KEY_GOOGLE=your-google-key  # Optional
```

### 3. Django Database Setup

```bash
cd backend/AutoGrader
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Access at http://localhost:8000
```

### 4. FastAPI Startup (separate terminal)

```bash
cd fastapi_app
uvicorn main:app --reload --port 8001
# Access API at http://localhost:8001
# Swagger UI at http://localhost:8001/docs
```

## Development Workflow

### Running Tests
```bash
make test          # Full test suite with coverage
make test-fast     # Quick tests without coverage
```

### Code Quality
```bash
make lint          # Check with flake8, black, mypy
make format        # Auto-format code
make clean         # Remove cache/artifacts
```

### Docker Development
```bash
make docker-build  # Build image
make docker-run    # Run container
docker-compose up  # Full stack with services
```

## Project Structure

```
AutoGrader/
├── backend/                    # Django application
│   ├── AutoGrader/
│   │   ├── settings.py        # Django settings (loads from .env)
│   │   └── ...
│   └── grader/
│       ├── views.py           # Updated with logging & retry logic
│       ├── models.py          # Task, LLMModel, TaskResult
│       └── ...
├── fastapi_app/               # FastAPI microservice
│   ├── main.py                # Refactored with all improvements
│   ├── schemas.py             # Pydantic models
│   ├── services/
│   │   ├── Config/
│   │   │   └── settings.py    # Pydantic settings
│   │   ├── logging_config.py  # JSON logging setup
│   │   ├── rag_service.py     # RAG singleton service
│   │   ├── utils.py           # Circuit breaker, retry logic
│   │   └── resources/         # RAG vector stores
│   ├── tests/
│   │   ├── conftest.py        # Pytest fixtures
│   │   ├── test_endpoints.py  # Endpoint tests
│   │   └── test_utils.py      # Utility tests
│   └── worker.py              # Celery tasks
├── .env.example               # Environment template
├── .gitignore                 # Excludes .env, secrets, cache
├── .github/
│   └── workflows/
│       └── tests.yml          # CI/CD pipeline
├── pyproject.toml             # Project configuration
├── Makefile                   # Build & dev commands
└── IMPROVEMENTS.md            # Detailed improvements guide
```

## API Endpoints

### Health Check
```bash
GET /health
# Response: {"status": "healthy", "version": "2.0.0", ...}
```

### List Models
```bash
GET /listall
# Returns available Ollama models
```

### Evaluate Code
```bash
POST /evaluate
Headers:
  Authorization: Bearer {token}
Form Data:
  task_id: 1
  theme: python_basics
  prog_lang: python
  model: gpt-4
  agent: evaluator-1
  api_key: {api-key}
Files:
  compressed_file: submission.zip
  rubrics_file: rubrics.json

# Response: {"message": "Task accepted", "task_id": 1, ...}
```

### Populate RAG
```bash
POST /examples/populate
{
  "theme": "python_basics",
  "examples": [
    {"id": 1, "code": "print('hello')"},
    {"id": 2, "code": "x = [1,2,3]"}
  ]
}
```

### Delete from RAG
```bash
POST /examples/delete
{
  "task_id": 1,
  "theme": "python_basics",
  "prog_lang": "python"
}
```

## Key Features

### 1. Security
- ✅ Pydantic input validation
- ✅ CORS configuration
- ✅ Bearer token authentication
- ✅ Environment-based secrets management
- ✅ SQL injection prevention (Django ORM)

### 2. Logging
- ✅ Structured JSON logging
- ✅ Configurable log levels
- ✅ Request/response logging
- ✅ Error tracking with context

### 3. Resilience
- ✅ Circuit breaker pattern
- ✅ Exponential backoff retry
- ✅ Connection pooling
- ✅ Health checks
- ✅ Timeout management

### 4. Performance
- ✅ Async/await support
- ✅ GZIP compression
- ✅ Singleton pattern caching
- ✅ Efficient file streaming

### 5. Testing
- ✅ 40+ unit tests
- ✅ Pytest fixtures
- ✅ Circuit breaker tests
- ✅ Endpoint validation tests
- ✅ Coverage reporting

### 6. Documentation
- ✅ Auto-generated OpenAPI/Swagger
- ✅ Comprehensive docstrings
- ✅ Type hints throughout
- ✅ API examples

### 7. DevOps
- ✅ GitHub Actions CI/CD
- ✅ Docker support
- ✅ Docker Compose
- ✅ Makefile automation
- ✅ Pre-commit hooks

## Configuration Details

### Django Settings
Located in `backend/AutoGrader/AutoGrader/settings.py`
- Loads `DJANGO_SECRET_KEY` from `.env`
- Loads `MICROSOFT_CLIENT_ID` and `MICROSOFT_CLIENT_SECRET` from `.env`
- SQLite by default (change in `.env` with `DATABASE_URL`)

### FastAPI Settings
Located in `fastapi_app/services/Config/settings.py`
- Pydantic v2.10 with full validation
- Loads all configuration from `.env`
- Configurable LLM backends
- RAG and Docker settings

### Logging Configuration
Located in `fastapi_app/services/logging_config.py`
- JSON format for log aggregation
- Configurable log levels
- Custom timestamp and context fields

## Troubleshooting

### Module not found: pydantic_settings
```bash
pip install pydantic-settings==2.1.0
```

### Port already in use
```bash
# Check what's using port 8001
lsof -i :8001
# Or use different port
uvicorn main:app --port 8002
```

### Database errors
```bash
cd backend/AutoGrader
python manage.py migrate
```

### File upload failures
- Ensure `fastapi_app/services/resources/` directory exists
- Check file permissions
- Verify disk space availability

## Testing

### Run all tests
```bash
make test
```

### Run specific test
```bash
cd fastapi_app
pytest tests/test_endpoints.py::TestEvaluateEndpoint::test_evaluate_success -v
```

### Generate coverage report
```bash
cd fastapi_app
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Production Deployment

### Using Docker
```bash
docker build -f Dockerfile -t autograder:2.0 .
docker run -p 8000:8000 -p 8001:8001 --env-file .env autograder:2.0
```

### Environment Variables (Production)
```env
FASTAPI_DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

### Security Checklist
- [ ] Change `DJANGO_SECRET_KEY`
- [ ] Set `FASTAPI_DEBUG=False`
- [ ] Configure ALLOWED_HOSTS in Django
- [ ] Use strong OAuth credentials
- [ ] Enable HTTPS
- [ ] Set up proper logging aggregation
- [ ] Configure database backups
- [ ] Set up monitoring/alerting

## Support & Documentation

- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **ReDoc Documentation**: http://localhost:8001/redoc
- **Improvements Guide**: See [IMPROVEMENTS.md](IMPROVEMENTS.md)
- **Issues**: Check GitHub repository

## License

MIT License - See LICENSE file for details

## Contributors

AutoGrader 2.0 - Comprehensive Improvements
