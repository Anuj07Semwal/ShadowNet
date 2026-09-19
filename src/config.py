import os
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: str | None = Field(default=None)
    pinecone_api_key: str | None = Field(default=None)
    google_api_key: str | None = Field(default=None)
    auth_username: str | None = Field(default=None, alias="SHADOWNET_AUTH_USERNAME")
    auth_password: str | None = Field(default=None, alias="SHADOWNET_AUTH_PASSWORD")
    auth_role: str = Field(default="investigator", alias="SHADOWNET_AUTH_ROLE")
    auth_reset_code: str | None = Field(default=None, alias="SHADOWNET_AUTH_RESET_CODE")
    auth_session_ttl_seconds: int = Field(default=28800, alias="SHADOWNET_AUTH_SESSION_TTL_SECONDS")
    auth_password_review_days: int = Field(default=45, alias="SHADOWNET_AUTH_PASSWORD_REVIEW_DAYS")
    auth_cookie_secure: bool = Field(default=False, alias="SHADOWNET_AUTH_COOKIE_SECURE")
    allow_runtime_embeddings: bool = Field(default=False, alias="ALLOW_RUNTIME_EMBEDDINGS")
    allowed_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        alias="ALLOWED_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {sorted(allowed)}")
        return value

    @field_validator("allowed_origins_raw")
    @classmethod
    def validate_allowed_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins:
            raise ValueError("ALLOWED_ORIGINS cannot be empty")
        return ",".join(origins)

    @property
    def allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
