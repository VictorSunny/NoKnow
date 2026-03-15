from logging import handlers
import os
import logging
from logging.config import dictConfig
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

LOG_DIR = BASE_DIR / ".logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG_JSON = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
        "standard": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s | %(levelname)s | %(message)s",
        },
        "error": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(pathname)s | %(message)s",
        },
        "access": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": '%(client_addr)s - "%(request_line)s" %(status_code)s,',
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
        "celery": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s | %(processName)s | %(levelname)s | %(name)s:\n %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "info_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "info.log"),
            "encoding": "utf-8",
            "maxBytes": 4_000_000,
            "backupCount": 4,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "error",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "encoding": "utf-8",
            "maxBytes": 4_000_000,
            "backupCount": 4,
        },
        "debug_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "error",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "encoding": "utf-8",
            "maxBytes": 4_000_000,
            "backupCount": 4,
        },
        "celery_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "celery",
            "filename": os.path.join(LOG_DIR, "celery.log"),
            "encoding": "utf-8",
            "maxBytes": 4_000_000,
            "backupCount": 4,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "info_file", "error_file", "debug_file"],
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "info_file", "error_file"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "ERROR",
            "handlers": ["console", "error_file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "info_file"],
            "level": "INFO",
            "formatter": "access",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "celery_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


def set_up_logging():
    dictConfig(LOGGING_CONFIG_JSON)
