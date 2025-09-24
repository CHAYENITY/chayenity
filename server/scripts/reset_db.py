from app.configs.app_config import app_config
import psycopg
import subprocess
import os

url = str(app_config.SQLALCHEMY_DATABASE_URI).replace("postgresql+asyncpg://", "postgresql://")
print("Connecting to:", url)
# Drop and recreate public schema
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        conn.commit()
        print("Dropped and recreated public schema")

# Run alembic stamp and upgrade using Poetry
cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print("Running alembic stamp and upgrade in", cwd)
# Ensure alembic thinks no migrations are applied, so upgrade will run the scripts
subprocess.check_call(["poetry", "run", "alembic", "stamp", "base"], cwd=cwd)
subprocess.check_call(["poetry", "run", "alembic", "upgrade", "head"], cwd=cwd)
print("Database reset and migrations applied")
