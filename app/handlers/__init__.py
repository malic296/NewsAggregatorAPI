from typing import Optional
from pathlib import Path
from app.repositories import LoggingRepository
from app.services import LoggingService
from .logging_handler import LoggingHandler, DatabaseLogger, FileLogger

def create_logging_handler(path: Optional[Path] = None) -> LoggingHandler:
    log_service: LoggingService = LoggingService(
        file_path = path if path else Path(__file__).parent.parent.parent / "api_errors.log",
        logging_repository = LoggingRepository()
    )

    db_logger = DatabaseLogger(log_service)
    file_logger = FileLogger(log_service)
    db_logger.set_next(file_logger)

    return db_logger