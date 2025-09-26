from app.configs.app_config import app_config
import psycopg

url = str(app_config.SQLALCHEMY_DATABASE_URI).replace('postgresql+asyncpg://','postgresql://')
print('Connecting to', url)
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables=[r[0] for r in cur.fetchall()]
        print('tables:', tables)
