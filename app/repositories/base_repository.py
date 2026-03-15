import atexit
import os
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path
from app.models.db_result import DBResult

class BaseRepository:
    _db_init: bool = False
    _pool: Optional[ConnectionPool] = None
    _conn_string: Optional[str] = None

    @classmethod
    def _read_env_vars(cls) -> None:
        if not cls._conn_string:
            try:
                load_dotenv(Path(__file__).parent.parent.parent / ".env")

                server = os.environ["SERVER"]
                user = os.environ["USER"]
                password = os.environ["PASSWORD"]
                database = os.environ["DATABASE"]
                port = os.environ["PORT"]
                address = os.environ["ADDRESS"]

                cls._conn_string = f"{server}://{user}:{password}@{address}:{port}/{database}"

            except KeyError as e:
                raise e

    @classmethod
    def _close_pool(cls) -> None:
        if cls._pool:
            cls._pool.close()
            cls._pool = None

    @classmethod
    def _get_pool(cls) -> ConnectionPool:
        if not cls._pool:
            cls._read_env_vars()
            try:
                cls._pool = ConnectionPool(
                    conninfo=cls._conn_string,
                    timeout=1.0,
                    open=True,
                    reconnect_failed=lambda pool: pool.close() if not cls._db_init else None

                )
                cls._pool.open()
                atexit.register(cls._close_pool)
            except Exception as e:
                raise e

        return cls._pool

    @classmethod
    def _setup_db(cls) -> None:
        if cls._db_init:
            return

        init_queries = [
            "CREATE TABLE IF NOT EXISTS channel ( id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, title TEXT, link TEXT UNIQUE );",
            "CREATE TABLE IF NOT EXISTS article ( id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, title TEXT, link TEXT UNIQUE, description TEXT, pub_date TIMESTAMPTZ, channel_id INTEGER REFERENCES channel(id) );",
            "CREATE TABLE IF NOT EXISTS logging ( id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ, status TEXT, module TEXT, method TEXT, message TEXT );",
            "CREATE TABLE IF NOT EXISTS password (id SERIAL PRIMARY KEY, hash TEXT NOT NULL);",
            "CREATE TABLE IF NOT EXISTS consumer (id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, username TEXT NOT NULL, email TEXT NOT NULL, password_id integer REFERENCES password(id) ON DELETE CASCADE);",
            "CREATE TABLE IF NOT EXISTS likes (id SERIAL PRIMARY KEY, consumer_id integer REFERENCES consumer(id) ON DELETE CASCADE, article_id integer REFERENCES article(id) ON DELETE CASCADE, UNIQUE (consumer_id, article_id));"

        ]

        pool = cls._get_pool()
        try:
            cls._db_init = True
            with pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    for query in init_queries:
                        cur.execute(query)

                conn.commit()

        except Exception as e:
            raise e

    def _execute(self, query: str, params: Optional[tuple] = None) -> DBResult:
        pool = self._get_pool()
        self._setup_db()
        try:
            with pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params or ())
                    data = []

                    if cur.description is not None:
                        data = cur.fetchall()

                    count = cur.rowcount
                    return DBResult(
                        success=True,
                        data=data,
                        row_count=count
                    )

        except Exception as e:
            return DBResult(
                success = False,
                error_message=e
            )