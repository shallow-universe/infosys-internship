import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def get_logger(name: str, log_file: str, level: str = "INFO"):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Rotating log file (5MB, keep 3 backups)
    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    sh = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
