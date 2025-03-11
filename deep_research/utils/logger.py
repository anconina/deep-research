# logger.py

import logging
import sys
import os
from logging import handlers

try:
    # Optional: colorlog for color-coded console logs
    import colorlog
    USE_COLORLOG = True
except ImportError:
    USE_COLORLOG = False

def set_logger(
    level: int = logging.DEBUG,
    log_to_file: bool = False,
    log_file_path: str = "app.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 3
):
    """
    Returns a configured logger with console and optional rotating file handlers.

    :param level: Logging level (e.g., logging.DEBUG, logging.INFO).
    :param log_to_file: Whether to enable file logging.
    :param log_file_path: The path to the log file.
    :param max_bytes: Max size (in bytes) of each log file before rotation.
    :param backup_count: Number of old log files to keep.
    :return: A configured logging.Logger instance.
    """

    # ----------------------------------------------------------------------------
    # FORMATTER
    # ----------------------------------------------------------------------------
    # Base log format
    log_format = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    handlers_list = []

    # If colorlog is installed, apply color formatting to console logs
    if USE_COLORLOG:
        formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s" + log_format,
            datefmt=date_format,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    else:
        formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # ----------------------------------------------------------------------------
    # CONSOLE HANDLER
    # ----------------------------------------------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    handlers_list.append(console_handler)

    # ----------------------------------------------------------------------------
    # FILE HANDLER (optional)
    # ----------------------------------------------------------------------------
    if log_to_file:
        file_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
        # Create a rotating file handler to automatically rotate logs when they get large
        file_handler = handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        handlers_list.append(file_handler)

    logging.basicConfig(level=level, format=log_format, datefmt=date_format,handlers=handlers_list)


# ---------------------------------------------------------------------
# USAGE EXAMPLE (remove or comment out for production):
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Create a logger that logs to console only
    set_logger(level=logging.DEBUG)
    logger_console = logging.getLogger(__name__)
    logger_console.info("This is an INFO message on the console logger.")
    logger_console.debug("This is a DEBUG message for console logger.")

    # Create a logger that logs to both console and a rotating file
    set_logger(level=logging.INFO, log_to_file=True, log_file_path="example.log")
    logger_file = logging.getLogger(__name__)
    logger_file.info("This message goes to the console and the file.")
    logger_file.error("Error message also goes to both console and file.")
