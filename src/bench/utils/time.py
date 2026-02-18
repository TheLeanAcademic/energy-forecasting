"""Time utilities."""
import time
from contextlib import contextmanager
from typing import Generator


@contextmanager
def timer(name: str = "Operation") -> Generator[dict, None, None]:
    """Context manager to measure execution time."""
    result = {"elapsed": 0.0}
    start = time.time()
    try:
        yield result
    finally:
        result["elapsed"] = time.time() - start


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"
