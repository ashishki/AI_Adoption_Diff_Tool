"""Shared structlog configuration and logger factory."""

from __future__ import annotations

from functools import lru_cache

import structlog
from structlog.typing import FilteringBoundLogger


@lru_cache(maxsize=1)
def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> FilteringBoundLogger:
    """Return a shared structured logger for the given component name."""
    _configure_structlog()
    return structlog.get_logger(name).bind(trace_id=None, operation_name=None)
