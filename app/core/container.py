from dataclasses import dataclass
from app.handlers import LoggingHandler
from app.services import DatabaseService, EmailService, SecurityService, CacheService

@dataclass(frozen=True)
class ServiceContainer:
    db: DatabaseService
    cache: CacheService
    email: EmailService
    security: SecurityService
    logger: LoggingHandler