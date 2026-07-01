"""Application configuration using Pydantic Settings."""

from typing import List

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="FraWo Radio Backend", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_env: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=4, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://radio:radio@localhost:5432/frawo_radio",
        description="PostgreSQL connection URL",
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=40, description="Max overflow connections")

    # Redis
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=50, description="Maximum Redis connections")

    # Security
    secret_key: str = Field(
        default="change-this-to-a-random-secret-key-in-production",
        description="Secret key for JWT",
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")

    # CORS — comma-separated string (pydantic-settings v2 requires JSON for List types)
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Allowed CORS origins (comma-separated)",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")

    # AzuraCast Integration
    azuracast_api_url: AnyHttpUrl = Field(
        default="https://radio-anker.hs27.internal/api", description="AzuraCast API URL"
    )
    azuracast_api_key: str = Field(
        default="your-azuracast-api-key", description="AzuraCast API key"
    )
    azuracast_station_id: int = Field(default=1, description="AzuraCast station ID")
    azuracast_verify_ssl: bool = Field(default=True, description="Verify SSL for AzuraCast")

    # Odoo ERP Integration (SSOT for partners, leads & supporter status)
    odoo_url: str = Field(default="http://10.1.0.112:8069", description="Odoo instance URL")
    odoo_db: str = Field(default="FraWo_GbR", description="Odoo database name")
    odoo_user: str = Field(default="wolf@frawo-tech.de", description="Odoo XML-RPC user email")
    odoo_password: str = Field(default="", description="Odoo XML-RPC password (set in .env!)")

    # Admin
    admin_api_key: str = Field(default="", description="Secret key for admin endpoints (set in .env!)")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Prometheus metrics port")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_burst: int = Field(default=10, description="Rate limit burst")

    # WebSocket
    ws_heartbeat_interval: int = Field(default=30, description="WebSocket heartbeat interval")
    ws_max_connections: int = Field(default=1000, description="Maximum WebSocket connections")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"


# Global settings instance
settings = Settings()