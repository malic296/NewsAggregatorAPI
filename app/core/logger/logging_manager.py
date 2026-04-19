from pathlib import Path
from typing import Optional
from enum import Enum
import logging
import sys
from logger.logger_handlers.database_logger import DatabaseLogger
from logger.fail_handler_wrapper import DropOnFailHandler

class LoggerMode(Enum):
    CONSOLE = 0
    FILE = 1
    DATABASE = 2
    ALL = 3

class LoggingManager:
    _initialized_app_logger = False
    def __init__(self, path: Optional[Path] = None, mode: LoggerMode = LoggerMode.CONSOLE):
        self.app_logger_prefix = "aggregator"
        self.log_format = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
        self.path = path if path else Path(__file__).parent.parent / "logs.log"
        self.mode = mode

    def _init_app_logger(self) -> None:
        if not LoggingManager._initialized_app_logger:
            app_logger = logging.getLogger(self.app_logger_prefix)
            app_logger.propagate = False
            logging.addLevelName(25, "SUCCESS")
            setattr(logging, "SUCCESS", 25)

            logging.getLogger("psycopg").setLevel(logging.CRITICAL)
            logging.getLogger("httpx").setLevel(logging.CRITICAL)

            def success(self, message, *args, **kws):
                if self.isEnabledFor(25):
                    self._log(25, message, args, **kws)

            logging.Logger.success = success
            app_logger.setLevel(logging.INFO)
            self._create_logger_handlers(app_logger)
            LoggingManager._initialized_app_logger = True

    def _create_logger_handlers(self, logger: logging.Logger) -> None:
        formatter = logging.Formatter(self.log_format)
        if self.mode in [LoggerMode.CONSOLE, LoggerMode.ALL]:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(formatter)
            logger.addHandler(DropOnFailHandler(h))

        if self.mode in [LoggerMode.FILE, LoggerMode.ALL] and self.path:
            h = logging.FileHandler(self.path)
            h.setFormatter(formatter)
            logger.addHandler(DropOnFailHandler(h))

        if self.mode in [LoggerMode.DATABASE, LoggerMode.ALL]:
            h = DatabaseLogger()
            logger.addHandler(DropOnFailHandler(h))

    def get_logger(self, name: str):
        if not LoggingManager._initialized_app_logger:
            self._init_app_logger()
        return logging.getLogger(self.app_logger_prefix + "." + name)
