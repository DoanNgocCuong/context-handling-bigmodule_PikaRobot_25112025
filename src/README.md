# Context Handling Service

Context Handling Service - Friendship Management Module for Pika Robot

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Application

```bash
# Development
uvicorn app.main_app:app --reload --host 0.0.0.0 --port 8000

# Or using Docker
docker-compose up
```

### 4. Test Health Check

```bash
curl http://localhost:8000/v1/health
```

## API Endpoints

### Health Check

- `GET /v1/health` - Check service health status

### Documentation

- `GET /docs` - Swagger UI (development only)
- `GET /redoc` - ReDoc documentation (development only)

## Project Structure

```
app/
├── core/              # Configuration, constants, exceptions
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response schemas
├── db/                # Database connection
├── repositories/      # Data access layer
├── services/          # Business logic layer
├── api/               # API routes and endpoints
├── cache/             # Caching layer
├── utils/             # Utility functions
└── main_app.py        # FastAPI application entry point
```

## Environment Variables

See `.env.example` for all available environment variables.

## Development

```bash
# Run tests
pytest

# Format code
black app/

# Lint code
flake8 app/
```

## License

Copyright © 2025 Pika Team
