import logging.config
import yaml
from pathlib import Path
from .formatters.traceback_formatter import TraceBackFormatter

def setup_logging():
    path = Path(__file__).parent / "logging.yaml"
    with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

    custom_formatter = TraceBackFormatter("%(asctime)s - %(levelname)s - %(module)s - %(method)s - %(message)s")

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(custom_formatter)

setup_logging()