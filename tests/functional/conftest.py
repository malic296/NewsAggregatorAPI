from datetime import datetime, timedelta, timezone
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
import os
import psycopg
from psycopg.rows import dict_row
from redis import Redis
from app.models import Consumer

@pytest.fixture
def mocked_consumer():
    return Consumer(id=1, uuid="uuid", username="username", email="email")

@pytest.fixture(scope="session")
def postgres_container_setup(request):
    os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
    postgres = PostgresContainer("postgres:16-alpine")
    postgres.start()

    def teardown():
        postgres.stop()

    request.addfinalizer(teardown)
    os.environ["SERVER"] = "postgresql"
    os.environ["USER"] = postgres.username
    os.environ["PASSWORD"] = postgres.password
    os.environ["ADDRESS"] = postgres.get_container_host_ip()
    os.environ["PORT"] = str(postgres.get_exposed_port(5432))
    os.environ["DATABASE"] = postgres.dbname
    os.environ["PEPPER"] = "pepper"

    conn_string = f"{os.environ["SERVER"]}://{os.environ['USER']}:{os.environ['PASSWORD']}@{os.environ['ADDRESS']}:{os.environ['PORT']}/{os.environ['DATABASE']}"

    with psycopg.connect(conn_string, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            #Table setup
            init_queries = [
                "CREATE TABLE IF NOT EXISTS channel ( id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, title TEXT, link TEXT UNIQUE );",
                "CREATE TABLE IF NOT EXISTS article ( id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, title TEXT, link TEXT UNIQUE, description TEXT, pub_date TIMESTAMPTZ, channel_id INTEGER REFERENCES channel(id) );",
                "CREATE TABLE IF NOT EXISTS logging ( id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ, status TEXT, module TEXT, method TEXT, message TEXT );",
                "CREATE TABLE IF NOT EXISTS password (id SERIAL PRIMARY KEY, hash TEXT NOT NULL);",
                "CREATE TABLE IF NOT EXISTS consumer (id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, username TEXT NOT NULL, email TEXT NOT NULL, password_id integer REFERENCES password(id) ON DELETE CASCADE);",
                "CREATE TABLE IF NOT EXISTS likes (id SERIAL PRIMARY KEY, consumer_id integer REFERENCES consumer(id) ON DELETE CASCADE, article_id integer REFERENCES article(id) ON DELETE CASCADE, UNIQUE (consumer_id, article_id));"
            ]
            for init in init_queries:
                cur.execute(init)

            # User setup
            query = """
                            WITH 
                            new_password AS (
                                INSERT INTO password(hash) VALUES (%s) RETURNING id, hash
                            ),
                            new_consumer AS (
                                INSERT INTO consumer(username, email, password_id, uuid)
                                SELECT %s, %s, id, %s FROM new_password
                                RETURNING id, uuid, username, email, password_id
                            )
                            SELECT nc.id, nc.uuid, nc.username, nc.email
                            FROM new_consumer nc
                            JOIN new_password np ON nc.password_id = np.id;
                        """

            params = (
                "$argon2id$v=19$m=65536,t=3,p=4$dPckrIJQedM7dB2PCJyxmQ$yF/gxyo/MeJ6/2Sc77VUFXOfHgyFurwya+88ofyonCg",
                "username",
                "email",
                "USER_1"
            )

            cur.execute(query, params)

            # Data setup
            query = "INSERT INTO channel(id, uuid, title, link) VALUES (%s, %s, %s, %s)"
            channel_1 = (1, "CHANNEL_1", "CHANNEL_TITLE_1", "CHANNEL_LINK_1")
            channel_2 = (2, "CHANNEL_2", "CHANNEL_TITLE_2", "CHANNEL_LINK_2")
            for channel in [channel_1, channel_2]:
                cur.execute(query, channel)

            query = "INSERT INTO article(id, uuid, title, link, description, pub_date, channel_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            article_1 = (1, "ARTICLE_1", "ARTICLE_TITLE_1", "ARTICLE_LINK_1", "ARTICLE_DESCRIPTION1", datetime.now(timezone.utc), 1)
            article_2 = (2, "ARTICLE_2", "ARTICLE_TITLE_2", "ARTICLE_LINK_2", "ARTICLE_DESCRIPTION2", datetime.now(timezone.utc) - timedelta(hours=10), 1)
            article_3 = (3, "ARTICLE_3", "ARTICLE_TITLE_3", "ARTICLE_LINK_3", "ARTICLE_DESCRIPTION3",datetime.now(timezone.utc), 2)

            for article in [article_1, article_2, article_3]:
                cur.execute(query, article)

@pytest.fixture(scope="function")
def db_connection():
    conn_string = f"{os.environ["SERVER"]}://{os.environ['USER']}:{os.environ['PASSWORD']}@{os.environ['ADDRESS']}:{os.environ['PORT']}/{os.environ['DATABASE']}"

    conn = psycopg.connect(conn_string, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()

@pytest.fixture(scope="session")
def redis_container_setup(request):
    os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
    redis = RedisContainer("redis:latest")
    redis.start()
    def teardown():
        redis.stop()

    request.addfinalizer(teardown)

    os.environ["REDIS_HOST"] = redis.get_container_host_ip()
    os.environ["REDIS_PORT"] = str(redis.get_exposed_port(6379))
    os.environ["REDIS_DB"] = "0"

@pytest.fixture(scope="function")
def cache_client():
    client = Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ["REDIS_PORT"]),
        db=int(os.environ["REDIS_DB"]),
        decode_responses=True
    )
    yield client
    client.flushall()

@pytest.fixture
def email_mock(mocker):
    os.environ["RESEND_API_KEY"] = "#####"
    mocker.patch("resend.Emails.send")
