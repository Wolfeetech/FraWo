# FraWo Radio Backend

Professional radio streaming backend built with FastAPI, PostgreSQL, and WebSocket support for real-time updates.

## Features

- 🎵 **Multi-station support** - Manage multiple radio stations from a single API
- 📡 **Real-time updates** - WebSocket connections for live now-playing information
- ⭐ **Track ratings** - User feedback and rating system with MongoDB storage
- 📊 **Analytics** - Listener tracking, play counts, and station statistics
- 🔄 **AzuraCast integration** - Seamless integration with AzuraCast streaming servers
- 📈 **Monitoring** - Prometheus metrics, structured logging with structlog
- 🔒 **Type-safe** - Full type hints with Pydantic v2 and mypy validation
- ✅ **Tested** - Comprehensive test suite with pytest and async support
- 🐳 **Docker-ready** - Production-ready Docker and docker-compose setup
- 📚 **API Documentation** - Auto-generated OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 (async)
- **Caching**: Redis 7
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio, httpx
- **Logging**: structlog
- **Monitoring**: Prometheus + Grafana
- **Code Quality**: ruff, black, mypy

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Poetry (for local development)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd apps/radio-backend

# Copy environment file
cp .env.example .env

# Edit .env and set your configuration
nano .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f backend
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:9090/metrics

### Option 2: Local Development

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Start PostgreSQL and Redis (via Docker)
docker-compose up -d postgres redis

# Run migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload

# Or use Make
make dev
```

## Configuration

All configuration is done via environment variables. See [.env.example](.env.example) for all available options.

### Key Configuration

```env
# Application
APP_NAME=FraWo Radio Backend
APP_ENV=production
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-secret-key-here

# AzuraCast
AZURACAST_API_URL=https://radio.example.com/api
AZURACAST_API_KEY=your-api-key
AZURACAST_STATION_ID=1

# CORS
CORS_ORIGINS=["https://frawo-funk.com","https://www.frawo-funk.com"]
```

## API Documentation

### Interactive Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

#### Stations

- `GET /api/stations/` - List all stations
- `GET /api/stations/{id}` - Get station by ID
- `GET /api/stations/slug/{slug}` - Get station by slug
- `POST /api/stations/` - Create new station
- `PATCH /api/stations/{id}` - Update station
- `DELETE /api/stations/{id}` - Delete station

#### Now Playing

- `GET /api/nowplaying/{station_id}` - Get current track for station
- `GET /api/nowplaying/` - Get all stations' now playing info

#### WebSocket

- `WS /api/ws/{station_id}` - Real-time updates for station

### Example Usage

```python
import httpx

# Get all stations
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/stations/")
    stations = response.json()

# Create a new station
station_data = {
    "name": "FraWo Funk",
    "slug": "frawo-funk",
    "stream_url": "https://radio.example.com/stream.mp3",
    "nowplaying_url": "https://radio.example.com/api/nowplaying",
    "location": "Rothkreuz",
    "icon": "📻"
}
response = await client.post("http://localhost:8000/api/stations/", json=station_data)
```

### WebSocket Example

```javascript
// Connect to station WebSocket
const ws = new WebSocket('ws://localhost:8000/api/ws/1');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    if (data.type === 'now_playing') {
        updateNowPlaying(data.data);
    }
};

ws.onopen = () => console.log('Connected to station 1');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

## Database Migrations

```bash
# Create a new migration
make migrate-create msg="add tracks table"
# or
poetry run alembic revision --autogenerate -m "add tracks table"

# Run migrations
make migrate-up
# or
poetry run alembic upgrade head

# Rollback last migration
make migrate-down
# or
poetry run alembic downgrade -1

# View migration history
make migrate-history
```

## Testing

```bash
# Run all tests
make test
# or
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_stations.py -v

# Watch mode (requires pytest-watch)
make test-watch
```

## Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make all
```

## Monitoring

### Prometheus Metrics

Metrics are exposed at `/metrics`:

```bash
curl http://localhost:9090/metrics
```

Key metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `http_requests_inprogress` - Active requests

### Structured Logging

All logs are output as structured JSON in production:

```json
{
    "event": "station_created",
    "level": "info",
    "timestamp": "2024-05-16T10:30:00Z",
    "station_id": 1,
    "name": "FraWo Funk",
    "app_name": "FraWo Radio Backend",
    "environment": "production"
}
```

### Grafana Dashboards

Start Grafana with monitoring profile:

```bash
docker-compose --profile monitoring up -d
```

Access Grafana at http://localhost:3000 (admin/admin)

## Project Structure

```
radio-backend/
├── app/
│   ├── api/              # API endpoints (routers)
│   │   ├── stations.py   # Station CRUD endpoints
│   │   ├── nowplaying.py # Now playing endpoints
│   │   └── websocket.py  # WebSocket endpoints
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings & environment
│   │   └── logging.py    # Structured logging setup
│   ├── db/               # Database configuration
│   │   └── base.py       # SQLAlchemy setup
│   ├── models/           # SQLAlchemy models
│   │   ├── station.py    # Station model
│   │   ├── track.py      # Track model
│   │   ├── rating.py     # Rating model
│   │   └── listener.py   # Listener model
│   ├── schemas/          # Pydantic schemas
│   │   ├── station.py    # Station schemas
│   │   ├── track.py      # Track schemas
│   │   └── rating.py     # Rating schemas
│   ├── services/         # Business logic
│   │   └── websocket.py  # WebSocket manager
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── tests/                # Test suite
│   ├── conftest.py      # Pytest configuration
│   └── test_stations.py # Station tests
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker Compose setup
├── pyproject.toml       # Poetry dependencies
├── Makefile             # Development commands
└── README.md            # This file
```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and test**
   ```bash
   make test
   make lint
   ```

3. **Create migration if needed**
   ```bash
   make migrate-create msg="add new field"
   make migrate-up
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add my feature"
   git push origin feature/my-feature
   ```

## Production Deployment

### Environment Setup

1. Set production environment variables
2. Use strong `SECRET_KEY`
3. Set `DEBUG=false`
4. Configure `CORS_ORIGINS` for your domain
5. Use production database credentials

### Docker Deployment

```bash
# Build production image
docker build -t frawo-radio-backend:latest .

# Run with production env
docker run -d \
  --name radio-backend \
  -p 8000:8000 \
  --env-file .env.production \
  frawo-radio-backend:latest
```

### Health Checks

The `/health` endpoint provides health status:

```bash
curl http://localhost:8000/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `make test`
6. Format code: `make format`
7. Submit a pull request

## License

Copyright © 2024 FraWo GbR. All rights reserved.

## Support

For issues and questions:
- GitHub Issues: https://github.com/frawo-tech/frawo/issues
- Documentation: https://docs.frawo-tech.de

---

Built with ❤️ by FraWo GbR
