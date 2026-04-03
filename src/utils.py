"""
Utility helpers shared across modules.
"""

import datetime


def timestamp_str() -> str:
    """Return an ISO-like timestamp suitable for filenames."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def seconds_to_mmss(seconds: float) -> str:
    """Convert seconds → 'MM:SS' string."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"
