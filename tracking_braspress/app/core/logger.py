import logging
import os
from logging.handlers import RotatingFileHandler

_CONFIGURED = False

def _ensure_logs_dir() -> str:
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    log_dir = _ensure_logs_dir()
    log_file = os.path.join(log_dir, "app.log")
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(fmt, datefmt))

    # Arquivo rotativo (5 MB x 3)
    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fmt, datefmt))

    root.addHandler(ch)
    root.addHandler(fh)
    _CONFIGURED = True

def get_logger(name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(name)
