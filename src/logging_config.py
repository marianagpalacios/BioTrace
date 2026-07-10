import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config import LOG_FILE_PATH


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)

MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


def configure_logging(
    log_file: str | Path = LOG_FILE_PATH,
) -> logging.Logger:
    """Configure a rotating file logger."""
    logger = logging.getLogger("biotrace")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    resolved_log_file = Path(
        log_file
    ).resolve()

    resolved_log_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    already_configured = any(
        isinstance(
            handler,
            RotatingFileHandler,
        )
        and Path(
            handler.baseFilename
        ).resolve() == resolved_log_file
        for handler in logger.handlers
    )

    if not already_configured:
        handler = RotatingFileHandler(
            resolved_log_file,
            maxBytes=MAX_LOG_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )

        handler.setFormatter(
            logging.Formatter(LOG_FORMAT)
        )

        logger.addHandler(handler)

    return logger