from pathlib import Path
from app.repositories import LoggingRepository
from typing import Optional
from datetime import datetime

class LoggingService:
    def __init__(self, file_path: Path, logging_repository: Optional[LoggingRepository] = None):
        self.file_path = file_path
        self.logging_repository = logging_repository

    def log_error_to_db(self, log: str) -> None:
        if not self.logging_repository:
            raise Exception("Logging repository init failed.")
        self.logging_repository.log_to_db(log)

    def log_error_to_file(self, log: str):
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write("\n" + str(datetime.now()) + " - " + log)