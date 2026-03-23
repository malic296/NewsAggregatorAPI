from fastapi.testclient import TestClient
import pytest
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container
from app.main import app
from app.models import Consumer

@pytest.fixture
def mocked_consumer() -> Consumer:
    return Consumer(id=1, uuid="1", username="username", email="email")

@pytest.fixture
def mock_services(mocker):
    mock = mocker.Mock()
    return mock

@pytest.fixture
def test_client(mocker, mocked_consumer, mock_services):
    mocker.patch("app.dependencies.auth.get_current_user", return_value=Consumer(id=1, uuid="1", username="username", email="email"))
    app.dependency_overrides[get_current_user] = lambda: mocked_consumer
    app.dependency_overrides[get_service_container] = lambda: mock_services
    return TestClient(app)
