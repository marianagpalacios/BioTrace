import logging
from pathlib import Path

from src.logging_config import configure_logging


def test_configure_logging_creates_log_file(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "biotrace.log"

    logger = configure_logging(log_path)
    logger.info("test message")

    for handler in logger.handlers:
        handler.flush()

    assert log_path.exists()

    assert "test message" in log_path.read_text(
        encoding="utf-8"
    )

    for handler in list(logger.handlers):
        if isinstance(
            handler,
            logging.FileHandler,
        ):
            handler.close()
            logger.removeHandler(handler)