import pytest
from app.services import EmailService, SecurityService

@pytest.fixture(scope="session")
def email_service():
    return EmailService()

@pytest.fixture(scope="session")
def security_service():
    return SecurityService()