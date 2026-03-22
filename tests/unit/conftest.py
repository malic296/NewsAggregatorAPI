import pytest
from app.services import EmailService, SecurityService, CacheService
from app.dependencies.logging import get_logging_handler
from app.schemas import RegistrationDTO

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