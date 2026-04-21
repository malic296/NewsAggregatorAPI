from .base_repository import BaseRepository
from datetime import datetime

class LoggingRepository(BaseRepository):
    def log_to_db(self, log):
        query = """
            INSERT INTO logging(timestamp, status, module, method, message) VALUES (%s, %s, %s, %s, %s)
        """
        params = (datetime.fromtimestamp(log.created), log.levelname, log.module, log.method, log.getMessage())

        result = self._execute(query, params)

        if not result.success:
            raise Exception(result.error_message)

        if not result.row_count:
            raise Exception("log_to_db method did not update any rows.")

