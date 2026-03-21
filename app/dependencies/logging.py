from app.handlers import LoggingHandler, FileLogger, DatabaseLogger
from app.repositories import LoggingRepository
from app.services import LoggingService
from pathlib import Path
from typing import Optional

def get_logging_handler(path: Optional[Path] = None, repo: Optional[LoggingRepository] = None) -> LoggingHandler:
    log_service: LoggingService = LoggingService(
        file_path = path if path else Path(__file__).parent.parent.parent / "api_errors.log", 
        logging_repository = repo if repo else LoggingRepository()
    )

    db_logger = DatabaseLogger(log_service)
    file_logger = FileLogger(log_service)
    db_logger.set_next(file_logger)

    return db_logger

