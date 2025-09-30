import logging
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from sqlmodel import SQLModel

from app.database.session import engine
from app.models import *  # type: ignore # noqa: F403

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(db_engine: AsyncEngine) -> None:
    try:
        async with db_engine.begin() as conn:
            logger.info("🧨 Dropping all tables...")

            # For PostgreSQL, we need to drop with CASCADE to handle enum dependencies
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

            # Enable PostGIS extension for geometry type
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

            logger.info("🛠 Creating all tables...")
            await conn.run_sync(SQLModel.metadata.create_all)

        # Optional test query
        async_session = async_sessionmaker(bind=db_engine, class_=AsyncSession)
        async with async_session() as session:
            await session.execute(text("SELECT 1"))

    except Exception as e:
        logger.error("❌ Database initialization failed: %s", e)
        raise e


async def main() -> None:
    logger.info("🔧 Initializing service (drop + create all tables)")
    await init(engine)
    logger.info("✅ Database is ready")


if __name__ == "__main__":
    asyncio.run(main())
