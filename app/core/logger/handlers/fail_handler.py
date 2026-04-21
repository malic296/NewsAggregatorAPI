import logging
import sys

class DropOnFailHandler(logging.Handler):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self._removed = False

    def emit(self, record):
        try:
            self.handler.emit(record)
        except Exception as e:
            if not self._removed:
                print(f"[CRITICAL] Loggers handler {self.handler.__class__.__name__} failed because: {e}", file=sys.stderr)
                root_logger = logging.getLogger(record.name)
                root_logger.removeHandler(self)
                self._removed = True


