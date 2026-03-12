from dataclasses import dataclass
from app.services import DatabaseService
from app.services.cache_service import CacheService
from app.services.email_service import EmailService
from app.services.security_service import SecurityService

@dataclass
class ServiceContainer:
    db: DatabaseService
    security: SecurityService
    cache: CacheService
    email: EmailService