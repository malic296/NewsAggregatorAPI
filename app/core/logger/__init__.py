import logging.config
import yaml
from pathlib import Path
from .database_logger import DatabaseLogger

def setup_logging():
    path = Path(__file__).parent / "logging.yaml"
    if path.exists():
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

setup_logging()