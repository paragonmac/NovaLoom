"""Performance timing utilities for NovaLoom.

Provides lightweight context managers and helpers for logging execution
latencies without introducing external dependencies.
"""
from __future__ import annotations
import time
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional
from functools import wraps

@dataclass
class PerfResult:
    label: str
    start: float
    end: float

    @property
    def ms(self) -> float:
        return (self.end - self.start) * 1000.0

@contextmanager
def time_block(label: str, logger: Optional[logging.Logger] = None, level: int = logging.INFO):
    """Context manager to time a code block.

    Parameters
    ----------
    label : str
        Description of the block.
    logger : logging.Logger, optional
        Logger to emit to; if None, uses root logger.
    level : int
        Logging level.
    """
    _logger = logger or logging.getLogger(__name__)
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        _logger.log(level, f"PERF {label} took {(end - start) * 1000.0:.1f} ms")

class PerfTimer:
    """Manual timer for ad-hoc measurements."""
    def __init__(self, label: str, logger: Optional[logging.Logger] = None, level: int = logging.INFO):
        self.label = label
        self.logger = logger or logging.getLogger(__name__)
        self.level = level
        self.start = time.perf_counter()
        self.end: Optional[float] = None

    def stop(self) -> PerfResult:
        if self.end is None:
            self.end = time.perf_counter()
            self.logger.log(self.level, f"PERF {self.label} took {(self.end - self.start)*1000.0:.1f} ms")
        return PerfResult(self.label, self.start, self.end)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
        return False

def log_timed(label: str | None = None, level: int = logging.INFO):
    """Decorator to log execution time of a function/method.

    Parameters
    ----------
    label : str | None
        Label to log; if None uses function __name__.
    level : int
        Logging level to emit at.
    """
    def decorator(func):
        _label = label or func.__name__
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                end = time.perf_counter()
                logging.getLogger(func.__module__).log(
                    level, f"PERF {_label} took {(end-start)*1000.0:.1f} ms"
                )
        return wrapper
    return decorator
