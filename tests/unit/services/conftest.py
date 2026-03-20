import pytest
from app.services import EmailService

@pytest.fixture
def email_service():
    return EmailService()