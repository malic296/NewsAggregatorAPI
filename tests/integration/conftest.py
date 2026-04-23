import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, get_services
from app.core.container import ServiceContainer
from app.models import Consumer
from run import app


@pytest.fixture
def consumer() -> Consumer:
    return Consumer(id=1, uuid="consumer-uuid", username="username", email="user@example.com")


@pytest.fixture
def mock_services(mocker):
    container = ServiceContainer(
        article_service=mocker.Mock(),
        channel_service=mocker.Mock(),
        consumer_service=mocker.Mock(),
        cache_service=mocker.Mock(),
        email_service=mocker.Mock(),
        security_service=mocker.Mock(),
    )
    container.cache_service.can_request_go_through.return_value = True
    container.channel_service.get_channels.return_value = []
    return container


@pytest.fixture
def test_client(consumer: Consumer, mock_services):
    app.dependency_overrides.clear()
    app.state.services = mock_services
    app.dependency_overrides[get_services] = lambda: mock_services
    app.dependency_overrides[get_current_user] = lambda: consumer
    client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(mock_services):
    app.dependency_overrides.clear()
    app.state.services = mock_services
    app.dependency_overrides[get_services] = lambda: mock_services
    client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
    yield client
    app.dependency_overrides.clear()
