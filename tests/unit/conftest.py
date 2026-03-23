from datetime import datetime, timezone
import pytest
from app.services import EmailService, SecurityService, CacheService, DatabaseService
from app.dependencies.logging import get_logging_handler
from app.schemas import RegistrationDTO
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository, LoggingRepository
from app.models import DBResult, Article, Channel, Consumer
from dataclasses import asdict

@pytest.fixture(scope="session")
def email_service():
    return EmailService()

@pytest.fixture(scope="session")
def security_service():
    return SecurityService()

@pytest.fixture
def logging_handler(tmp_path):
    return get_logging_handler(tmp_path)

@pytest.fixture
def mocked_redis(mocker, monkeypatch):
    mock_class = mocker.patch("redis.Redis")
    
    mock_instance = mock_class.return_value
    
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")

    mock_instance.ping.return_value = True

    return mock_instance

@pytest.fixture
def cache_service(mocked_redis):
    return CacheService()

@pytest.fixture
def registration_dto():
    return RegistrationDTO(username="username", email="email", password="password")

@pytest.fixture
def db_service():
    return DatabaseService(articles=ArticleRepository(), channels=ChannelRepository(), consumers=ConsumerRepository())

@pytest.fixture(scope="session")
def article_repository():
    return ArticleRepository()

@pytest.fixture(scope="session")
def channel_repository():
    return ChannelRepository()

@pytest.fixture(scope="session")
def consumer_repository():
    return ConsumerRepository()

@pytest.fixture(scope="session")
def logging_repository():
    return LoggingRepository()

@pytest.fixture
def invalid_db_result() -> DBResult:
    return DBResult(
        success=False,
        error_message="INVALID_DB_RESULT_MESSAGE",
        data=None,
        row_count=0
    )

@pytest.fixture
def db_result_articles() -> DBResult:
    articles = [
        Article(id=1, uuid="1", title="TITLE_1", link="LINK_1", description="DESCRIPTION_1", pub_date=datetime.now(timezone.utc), channel_link="CHANNEL_LINK1", likes=1, liked_by_user=False),
        Article(id=2, uuid="2", title="TITLE_2", link="LINK_2", description="DESCRIPTION_2",pub_date=datetime.now(timezone.utc), channel_link="CHANNEL_LINK2", likes=2, liked_by_user=False),
    ]

    return DBResult(
        success=True,
        data=[asdict(article) for article in articles],
        row_count=len(articles)
    )

@pytest.fixture
def db_result_channels() -> DBResult:
    channels = [
        Channel(id=1, uuid="1", title="TITLE_1", link="CHANNEL_LINK1"),
        Channel(id=2, uuid="2", title="TITLE_2", link="CHANNEL_LINK2"),
    ]

    return DBResult(
        success=True,
        data=[asdict(channel) for channel in channels],
        row_count=len(channels)
    )

@pytest.fixture
def db_result_id() -> DBResult:
    return DBResult(
        success=True,
        data=[{"id": 1}],
        row_count=1
    )

@pytest.fixture
def db_result_consumer() -> DBResult:
    consumer = Consumer(id=1, uuid="1", username="username", email="email")

    return DBResult(
        success=True,
        data=[asdict(consumer)],
        row_count=1
    )

@pytest.fixture
def db_result_none() -> DBResult:
    return DBResult(
        success=True,
        data=None,
        row_count=1
    )