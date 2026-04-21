import logging
import traceback
import os

class TraceBackFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        ex = getattr(record, 'exception', None)

        if ex:
            tb_obj = ex[2] if isinstance(ex, tuple) else getattr(ex, '__traceback__', None)

            if tb_obj:
                frames = traceback.extract_tb(tb_obj)
                record.module = os.path.basename(frames[-1].filename)

                record.method = frames[-1].name

        if not hasattr(record, 'module'):
            record.module = record.name

        if not hasattr(record, 'method'):
            record.method = record.funcName

        return super().format(record)