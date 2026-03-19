from app.handlers import LoggingHandler, FileLogger, DatabaseLogger
from app.repositories import LoggingRepository
from app.services import LoggingService
from pathlib import Path


def get_logging_handler() -> LoggingHandler:
    try:
        repo = LoggingRepository()
    except Exception as e:
        repo = None

    log_service: LoggingService = LoggingService(Path(__file__).parent.parent.parent / "api_errors.log", logging_repository=repo)

    db_logger = DatabaseLogger(log_service)
    file_logger = FileLogger(log_service)
    db_logger.set_next(file_logger)

    return db_logger

