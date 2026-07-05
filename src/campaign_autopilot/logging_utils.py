"""Structured logging for Campaign Autopilot.

Provides consistent logging across all agents with level control,
structured fields, and optional file output.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

_DEFAULT_LEVEL = os.environ.get("AUTOPILOT_LOG_LEVEL", "INFO").upper()
_DEFAULT_FORMAT = "%(asctime)s [%(levelname)-5s] %(name)s: %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def get_log_dir() -> Path:
    p = Path(os.environ.get("AUTOPILOT_LOG_DIR", ".state/logs"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def configure_logging(
    level: str = _DEFAULT_LEVEL,
    log_file: str | None = None,
    component: str = "autopilot",
) -> logging.Logger:
    """Configure and return a structured logger for a component."""
    logger = logging.getLogger(component)
    logger.setLevel(LOG_LEVELS.get(level, logging.INFO))
    logger.handlers.clear()

    fmt = logging.Formatter(_DEFAULT_FORMAT, datefmt=_DEFAULT_DATE_FORMAT)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler
    if log_file is None:
        log_file = str(get_log_dir() / f"{component}.log")
    fh = logging.FileHandler(log_file, mode="a")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


class StructuredLogger:
    """Logger that produces structured JSON logs for machine parsing."""

    def __init__(self, component: str, log_dir: str | Path | None = None):
        self.component = component
        self.log_dir = Path(log_dir) if log_dir else get_log_dir()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self.log_dir / f"{component}.jsonl"
        self._file = open(self._log_path, "a")  # noqa: SIM115

    def _emit(self, level: str, message: str, **fields: Any) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": self.component,
            "level": level,
            "message": message,
            **fields,
        }
        self._file.write(json.dumps(record) + "\n")
        self._file.flush()

    def debug(self, msg: str, **kw: Any) -> None:
        self._emit("DEBUG", msg, **kw)

    def info(self, msg: str, **kw: Any) -> None:
        self._emit("INFO", msg, **kw)

    def warning(self, msg: str, **kw: Any) -> None:
        self._emit("WARNING", msg, **kw)

    def error(self, msg: str, **kw: Any) -> None:
        self._emit("ERROR", msg, **kw)

    def close(self) -> None:
        self._file.close()

    def __del__(self) -> None:
        try:
            self._file.close()
        except Exception:
            pass
