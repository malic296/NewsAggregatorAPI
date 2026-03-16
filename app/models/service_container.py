from dataclasses import dataclass
from app.services import DatabaseService, CacheService, EmailService, SecurityService

@dataclass
class ServiceContainer:
    db: DatabaseService
    security: SecurityService
    cache: CacheService
    email: EmailService