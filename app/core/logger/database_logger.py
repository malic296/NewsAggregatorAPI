import logging

class DatabaseLogger(logging.Handler):
    def __init__(self, writer_func):
        super().__init__()
        self.writer_func = writer_func

    def emit(self, record):
        self.writer_func(record)