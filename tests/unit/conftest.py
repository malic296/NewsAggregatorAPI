import pytest
from app.services import EmailService, SecurityService
from app.dependencies.logging import get_logging_handler

@pytest.fixture(scope="session")
def email_service():
    return EmailService()

@pytest.fixture(scope="session")
def security_service():
    return SecurityService()

@pytest.fixture
def logging_handler(tmp_path):
    return get_logging_handler(tmp_path)