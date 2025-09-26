from typing import Literal
from pydantic import (
    AnyUrl,
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


# Ensure environment variables from .env are loaded into os.environ so
# Pydantic Settings can pick them up when instantiating AppConfig. This is a
# lightweight, dependency-free loader (avoids adding python-dotenv).
def _load_dotenv_file(dotenv_path: str = ".env") -> None:
    p = Path(dotenv_path)
    if not p.exists():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # don't overwrite existing environment variables
        if key not in os.environ:
            os.environ[key] = val


# load .env early
_load_dotenv_file()

# TODO: SETUP DB


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str = "CHAYENITY"
    API_STR: str = "/api"

    REFRESH_SECRET_KEY: str = "refresh_secret_key"
    REFRESH_TOKEN_EXPIRE: int = 10080
    ACCESS_SECRET_KEY: str = "access_secret_key"
    ACCESS_TOKEN_EXPIRE: int = 10080
    ALGORITHM: str = "HS256"

    FRONTEND_URL: str = ""
    BACKEND_URL: list[AnyUrl] | str = []

    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        if isinstance(self.BACKEND_URL, str):
            return self.BACKEND_URL.split(",") + [self.FRONTEND_URL]
        return [str(origin) for origin in self.BACKEND_URL] + [self.FRONTEND_URL]

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        uri = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"  # * Asynchronous
            # f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}" # * Synchronous
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return PostgresDsn(uri)


app_config = AppConfig()  # type: ignore[call-arg]
