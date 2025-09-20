import asyncio
import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.configs.app_config import app_config
from sqlmodel import SQLModel
from app.models import *  # type: ignore # noqa: F403

# Alembic Config
config = context.config

# Setup loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata
target_metadata = SQLModel.metadata

# Convert async URL to sync URL for Alembic migrations
sync_url = str(app_config.SQLALCHEMY_DATABASE_URI).replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode using sync engine."""
    # Use sync engine for migrations
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("No sqlalchemy.url configured")
    
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


main()
