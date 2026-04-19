from models.log import Log
from logging import Handler
from repositories.logging_repository import LoggingRepository
from datetime import datetime
from models.error import LoggingError

class DatabaseLogger(Handler):
    def __init__(self):
        super().__init__()
        self.setup = False
        self.log_repo = None

    def setup_repo(self) -> None:
        self.setup = True
        try:
            self.log_repo = LoggingRepository()
        except Exception as e:
            raise LoggingError(f"Failed setting up logging repository because: {e}")

    def emit(self, record) -> None:
        if not self.setup:
            self.setup_repo()

        log_time = datetime.fromtimestamp(record.created)

        log: Log = Log(
            log_time,
            record.levelname,
            record.name,
            record.funcName,
            str(record.msg)
        )

        result = self.log_repo.log(log)
        if not result.success:
            raise LoggingError(f"Failed logging to DB because: {result.error_message if result.error_message else "Unknown error"}")
