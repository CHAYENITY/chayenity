from typing import Literal
from pydantic import (
    AnyUrl,
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ENVIRONMENT: Literal["local", "staging", "production", "test"] = "local"
    PROJECT_NAME: str
    API_STR: str

    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE: int
    ACCESS_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE: int
    ALGORITHM: str

    FRONTEND_URL: str
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
