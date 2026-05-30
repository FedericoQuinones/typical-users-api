import os

from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Missing required environment variable DATABASE_URL")

pool = AsyncConnectionPool(DATABASE_URL, open=False)
