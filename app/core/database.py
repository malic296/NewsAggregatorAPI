from psycopg_pool import ConnectionPool
from .settings import Settings

def create_connection_pool(settings: Settings) -> ConnectionPool:
    conn_string = f"{settings.db_server}://{settings.db_user}:{settings.db_password}@{settings.db_address}:{settings.db_port}/{settings.db_name}"

    return ConnectionPool(
        conn_string,
        timeout=1.0,
        open=True
    )