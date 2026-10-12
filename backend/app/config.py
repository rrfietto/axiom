import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    api_prefix: str
    cors_origins: tuple[str, ...]


def _parse_origins(value: str) -> tuple[str, ...]:
    return tuple(origin.strip() for origin in value.split(",") if origin.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Axiom API"),
        environment=os.getenv("ENVIRONMENT", "development"),
        api_prefix=os.getenv("API_PREFIX", "/api"),
        cors_origins=_parse_origins(os.getenv("CORS_ORIGINS", "http://localhost:5173")),
    )
