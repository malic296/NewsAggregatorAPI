from abc import ABC ,abstractmethod

class LoggingHandler(ABC):
    def __init__(self, logging_service):
        self.logging_service = logging_service
        self.next_handler = None

    @abstractmethod
    def _do_logic(self, log) -> None:
        pass

    def handle(self, log: str) -> None:
        try:
            self._do_logic(log)
        except Exception as e:
            if self.next_handler:
                self.next_handler.handle(log)
            else:
                print(f"CRITICAL: All logging methods failed. Original error: {e}")

    def set_next(self, handler: LoggingHandler):
        self.next_handler = handler

class DatabaseLogger(LoggingHandler):
    def _do_logic(self, log) -> None:
        self.logging_service.log_error_to_db(log)

class FileLogger(LoggingHandler):
    def _do_logic(self, log) -> None:
        self.logging_service.log_error_to_file(log)