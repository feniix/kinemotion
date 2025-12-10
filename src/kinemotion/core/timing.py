"""Timing utilities for performance profiling."""

import time
from collections.abc import Generator
from contextlib import contextmanager


class PerformanceTimer:
    """Simple timer for tracking execution duration of named steps.

    Uses context manager pattern for clean, testable timing instrumentation.
    Accumulates timing data in metrics dictionary accessible via get_metrics().
    """

    def __init__(self) -> None:
        """Initialize timer with empty metrics dictionary."""
        self.metrics: dict[str, float] = {}

    @contextmanager
    def measure(self, name: str) -> Generator[None, None, None]:
        """Context manager to measure execution time of a block.

        Args:
            name: Name of the step being measured (e.g., "pose_tracking")

        Yields:
            None

        Example:
            timer = PerformanceTimer()
            with timer.measure("video_initialization"):
                # code to measure
                pass
            metrics = timer.get_metrics()  # {"video_initialization": 0.123}
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics[name] = duration

    def get_metrics(self) -> dict[str, float]:
        """Get collected timing metrics in seconds.

        Returns:
            A copy of the metrics dictionary to prevent external modification.
        """
        return self.metrics.copy()
