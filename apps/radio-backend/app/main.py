"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import nowplaying, stations, websocket
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

# Configure logging before anything else
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

    yield

    # Shutdown
    logger.info("application_shutting_down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## FraWo Radio Backend API

    Professional radio streaming backend with FastAPI, PostgreSQL, and real-time WebSocket support.

    ### Features

    * 🎵 **Multi-station support** - Manage multiple radio stations
    * 📡 **Real-time updates** - WebSocket connections for live now-playing info
    * ⭐ **Track ratings** - User feedback and track rating system
    * 📊 **Analytics** - Listener tracking and statistics
    * 🔄 **AzuraCast integration** - Seamless integration with AzuraCast streaming
    * 📈 **Monitoring** - Prometheus metrics and structured logging

    ### Documentation

    * **Interactive API docs**: `/docs` (Swagger UI)
    * **Alternative docs**: `/redoc` (ReDoc)
    * **OpenAPI spec**: `/openapi.json`

    ### Support

    For issues and questions, visit our [GitHub repository](https://github.com/frawo-tech/frawo).
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics — must be at module level before app starts
if settings.enable_metrics:
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/docs", "/redoc", "/openapi.json"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")

# Include routers
app.include_router(stations.router, prefix="/api")
app.include_router(nowplaying.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """
    Root endpoint.

    Returns basic API information.
    """
    return JSONResponse(
        content={
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "docs": "/docs",
            "health": "/health",
        }
    )


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns the health status of the application and its dependencies.

    Used by Docker, Kubernetes, and monitoring systems.
    """
    # TODO: Add actual health checks for database, redis, etc.
    health_status = {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "checks": {
            "api": "healthy",
            "database": "unknown",  # TODO: Check PostgreSQL connection
            "redis": "unknown",  # TODO: Check Redis connection
        },
    }

    logger.debug("health_check_requested", status=health_status["status"])
    return JSONResponse(content=health_status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
