from fastapi.testclient import TestClient
import pytest

from app.dependencies.auth import get_current_user, get_rate_limiter
from app.dependencies.service_container import get_service_container
from run import app
from app.models import Consumer

@pytest.fixture
def mocked_consumer() -> Consumer:
    return Consumer(id=1, uuid="1", username="username", email="email")

@pytest.fixture
def mock_services(mocker):
    mock = mocker.Mock()
    return mock

@pytest.fixture
def test_client(mocked_consumer, mock_services):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = lambda: mocked_consumer
    app.dependency_overrides[get_service_container] = lambda: mock_services
    return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def test_client_without_jwt(mock_services):
    app.dependency_overrides.clear()
    mock_services.security.decode_access_token.return_value = None
    app.dependency_overrides[get_service_container] = lambda: mock_services
    return TestClient(app, raise_server_exceptions=False)
