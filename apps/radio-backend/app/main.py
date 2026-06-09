"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.api import community, nowplaying, stations, websocket
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.base import AsyncSessionLocal

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
    if settings.is_production:
        if not settings.admin_api_key:
            logger.error("STARTUP_MISCONFIGURATION: ADMIN_API_KEY is not set in production!")
        if settings.secret_key == "change-this-to-a-random-secret-key-in-production":
            logger.error("STARTUP_MISCONFIGURATION: SECRET_KEY is still the default value!")

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
_is_prod = settings.is_production

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=None,      # served manually below — disabled in production
    redoc_url=None,
    openapi_url=None,   # also served manually — hidden in production
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
app.include_router(community.router, prefix="/api/v1")


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
            "health": "/health",
        }
    )


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    checks: dict[str, str] = {"api": "healthy"}

    # Database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as exc:
        checks["database"] = f"unhealthy: {exc}"
        logger.error("health_check_db_failed", error=str(exc))

    # Redis (optional — not critical if unused)
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(str(settings.redis_url), socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        checks["redis"] = "healthy"
    except Exception:
        checks["redis"] = "unavailable"

    overall = "healthy" if checks["database"] == "healthy" else "degraded"
    status_code = 200 if overall == "healthy" else 503

    logger.debug("health_check_requested", status=overall)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "app": settings.app_name,
            "checks": checks,
        },
    )


def _check_docs_access(x_admin_key: str = Header(default="")) -> None:
    if _is_prod:
        key = settings.admin_api_key
        if not key or x_admin_key != key:
            raise HTTPException(status_code=404, detail="Not Found")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(x_admin_key: str = Header(default="")):
    _check_docs_access(x_admin_key)
    return get_openapi(title=settings.app_name, version=settings.app_version, routes=app.routes)


@app.get("/docs", include_in_schema=False)
async def swagger_ui(x_admin_key: str = Header(default="")):
    _check_docs_access(x_admin_key)
    return get_swagger_ui_html(openapi_url="/openapi.json", title=f"{settings.app_name} — Docs")


@app.get("/redoc", include_in_schema=False)
async def redoc(x_admin_key: str = Header(default="")):
    _check_docs_access(x_admin_key)
    return get_redoc_html(openapi_url="/openapi.json", title=f"{settings.app_name} — ReDoc")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
