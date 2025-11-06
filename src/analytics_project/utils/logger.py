"""Provide centralized logging for professional analytics projects.

This module configures project-wide logging to track events, debug issues,
and maintain audit trails during data analysis workflows.
"""

import pathlib
import sys

from loguru import logger

_is_configured: bool = False
_log_file_path: pathlib.Path | None = None


def _project_root(start: pathlib.Path | None = None) -> pathlib.Path:
    """Find the project root by walking up until we see a pyproject.toml or .git.

    Falls back to the directory containing this file.
    """
    here = (start or pathlib.Path(__file__)).resolve()
    for p in [here, *here.parents]:
        if (p / "pyproject.toml").exists() or (p / ".git").exists():
            return p
    return here.parent  # fallback


project_root = _project_root()


def get_log_file_path() -> pathlib.Path:
    """Return the path to the active log file, or default path if not initialized."""
    if _log_file_path is not None:
        return _log_file_path
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir / "app.log"


def configure_logger(script_name: str = "app") -> None:
    """Configure the Loguru logger for the application."""
    global _is_configured, _log_file_path

    if _is_configured:
        return

    # Create logs directory
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Define log file path
    _log_file_path = logs_dir / f"{script_name}.log"

    # Remove default handler
    logger.remove()

    # Add colorized console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # Add file handler
    logger.add(
        _log_file_path,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
    )

    logger.info(f"Logger configured. Logging to: {_log_file_path}")
    _is_configured = True


# Auto-configure with default name if imported
if not _is_configured:
    configure_logger()
