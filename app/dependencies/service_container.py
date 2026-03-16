from app.models import ServiceContainer
from app.services import DatabaseService, CacheService, EmailService, SecurityService

def get_service_container() -> ServiceContainer:
    return ServiceContainer(
        db=DatabaseService(),
        security=SecurityService(),
        cache=CacheService(),
        email=EmailService()
    )