"""Timing utilities for performance profiling.

This module implements a hybrid instrumentation pattern combining:
1. Protocol-based type safety (structural subtyping)
2. Null Object Pattern (zero overhead when disabled)
3. High-precision timing (time.perf_counter)
4. Memory optimization (__slots__)
5. Accumulation support (for loops and repeated measurements)

Performance Characteristics:
    - PerformanceTimer overhead: ~200ns per measurement
    - NullTimer overhead: ~20ns per measurement
    - Memory: 32 bytes per timer instance
    - Precision: ~1 microsecond (perf_counter)

Example:
    # Active timing
    timer = PerformanceTimer()
    with timer.measure("video_processing"):
        process_video(frames)
    metrics = timer.get_metrics()

    # Zero-overhead timing (disabled)
    tracker = PoseTracker(timer=NULL_TIMER)
    # No timing overhead, but maintains API compatibility
"""

import time
from contextlib import AbstractContextManager, ExitStack, contextmanager
from typing import Protocol, runtime_checkable

# OpenTelemetry related imports, guarded by try-except for optional dependency
_trace_module = None  # This will hold the actual 'trace' module if imported
_otel_tracer_class = None  # This will hold the actual 'Tracer' class if imported

try:
    import opentelemetry.trace as _trace_module_import  # Import the module directly

    _otel_tracer_class = (
        _trace_module_import.Tracer
    )  # Get the Tracer class from the module
    _trace_module = (
        _trace_module_import  # Expose the trace module globally after successful import
    )
except ImportError:
    pass  # No OTel, so these remain None

# Now define the global/module-level variables used elsewhere
# Conditionally expose 'trace' and 'Tracer' aliases
trace = _trace_module  # This will be the actual module or None


class Tracer:  # Dummy for type hints if actual Tracer is not available
    pass


if _otel_tracer_class:
    Tracer = _otel_tracer_class  # Override dummy if actual Tracer is available

# This _OPENTELEMETRY_AVAILABLE variable is assigned only once,
# after the try-except block
_OPENTELEMETRY_AVAILABLE = bool(
    _otel_tracer_class
)  # True if Tracer class was successfully loaded


@runtime_checkable
class Timer(Protocol):
    """Protocol for timer implementations.

    Enables type-safe substitution of PerformanceTimer with NullTimer.
    Uses structural subtyping - any class implementing these methods
    conforms to the protocol.
    """

    def measure(self, name: str) -> AbstractContextManager[None]:
        """Context manager to measure execution time of a block.

        Args:
            name: Name of the step being measured (e.g., "pose_tracking")

        Returns:
            Context manager that measures execution time
        """
        ...

    def get_metrics(self) -> dict[str, float]:
        """Retrieve all collected timing metrics.

        Returns:
            Dictionary mapping operation names to durations in seconds
        """
        ...


class _NullContext(AbstractContextManager[None]):
    """Singleton null context manager with zero overhead.

    Implements the context manager protocol but performs no operations.
    Optimized away by the Python interpreter for minimal overhead.
    """

    __slots__ = ()

    def __enter__(self) -> None:
        """No-op entry - returns immediately."""
        return None

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
        """No-op exit - returns immediately.

        Args:
            exc_type: Exception type (ignored)
            exc_val: Exception value (ignored)
            exc_tb: Exception traceback (ignored)

        Returns:
            False (does not suppress exceptions)
        """
        return False


class NullTimer:
    """No-op timer implementing the Null Object Pattern.

    Provides zero-overhead instrumentation when profiling is disabled.
    All methods are no-ops that optimize away at runtime.

    Performance: ~20-30 nanoseconds overhead per measure() call.
    This is negligible compared to any actual work being measured.

    Use Cases:
        - Production deployments (profiling disabled)
        - Performance-critical paths
        - Testing without timing dependencies

    Example:
        # Use global singleton for zero allocation overhead
        tracker = PoseTracker(timer=NULL_TIMER)

        # No overhead - measure() call optimizes to nothing
        with tracker.timer.measure("operation"):
            do_work()
    """

    __slots__ = ()

    def measure(self, name: str) -> AbstractContextManager[None]:
        """Return a no-op context manager.

        This method does nothing and is optimized away by the Python interpreter.
        The context manager protocol (__enter__/__exit__) has minimal overhead.

        Args:
            name: Ignored - kept for protocol compatibility

        Returns:
            Singleton null context manager
        """
        return _NULL_CONTEXT

    def get_metrics(self) -> dict[str, float]:
        """Return empty metrics dictionary.

        Returns:
            Empty dictionary (no metrics collected)
        """
        return {}


# Singleton instances for global reuse
# Use these instead of creating new instances to avoid allocation overhead
_NULL_CONTEXT = _NullContext()
NULL_TIMER: Timer = NullTimer()


class _MeasureContext(AbstractContextManager[None]):
    """Optimized context manager for active timing.

    Uses __slots__ for memory efficiency and perf_counter for precision.
    Accumulates durations for repeated measurements of the same operation.
    """

    __slots__ = ("_metrics", "_name", "_start")

    def __init__(self, metrics: dict[str, float], name: str) -> None:
        """Initialize measurement context.

        Args:
            metrics: Dictionary to store timing results
            name: Name of the operation being measured
        """
        self._metrics = metrics
        self._name = name
        self._start = 0.0

    def __enter__(self) -> None:
        """Start timing measurement using high-precision counter."""
        self._start = time.perf_counter()
        return None

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
        """Complete timing measurement and accumulate duration.

        Accumulates duration if the same operation is measured multiple times.
        This is useful for measuring operations in loops.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            False (does not suppress exceptions)
        """
        duration = time.perf_counter() - self._start
        # Accumulate for repeated measurements (e.g., in loops)
        self._metrics[self._name] = self._metrics.get(self._name, 0.0) + duration
        return False


class PerformanceTimer:
    """High-precision timer for tracking execution duration of named steps.

    Uses time.perf_counter() for high-resolution monotonic timing.
    Suitable for development, profiling, and performance analysis.

    Accumulates timing data for repeated measurements of the same operation,
    making it suitable for measuring operations in loops.

    Precision: ~1 microsecond on most platforms
    Overhead: ~200 nanoseconds per measurement

    Example:
        timer = PerformanceTimer()

        # Measure single operation
        with timer.measure("video_initialization"):
            initialize_video(path)

        # Measure in loop (accumulates)
        for frame in frames:
            with timer.measure("pose_tracking"):
                track_pose(frame)

        metrics = timer.get_metrics()
        print(f"Total pose tracking: {metrics['pose_tracking']:.3f}s")
    """

    __slots__ = ("metrics",)

    def __init__(self) -> None:
        """Initialize timer with empty metrics dictionary."""
        self.metrics: dict[str, float] = {}

    def measure(self, name: str) -> AbstractContextManager[None]:
        """Context manager to measure execution time of a block.

        Uses perf_counter() for high-resolution monotonic timing.
        More precise and reliable than time.time() for performance measurement.

        Args:
            name: Name of the step being measured (e.g., "pose_tracking")

        Returns:
            Context manager that measures execution time

        Note:
            perf_counter() is monotonic - not affected by system clock adjustments.
            Repeated measurements of the same operation name will accumulate.
        """
        return _MeasureContext(self.metrics, name)

    def get_metrics(self) -> dict[str, float]:
        """Get collected timing metrics in seconds.

        Returns:
            A copy of the metrics dictionary to prevent external modification.
        """
        return self.metrics.copy()


@contextmanager
def _composite_context_manager(contexts: list[AbstractContextManager[None]]):
    """Helper to combine multiple context managers into one.

    Uses ExitStack to manage entering and exiting multiple contexts transparently.
    """
    with ExitStack() as stack:
        for ctx in contexts:
            stack.enter_context(ctx)
        yield


class CompositeTimer:
    """Timer that delegates measurements to multiple underlying timers.

    Useful for enabling both local performance timing (for JSON output)
    and distributed tracing (OpenTelemetry) simultaneously.
    """

    __slots__ = ("timers",)

    def __init__(self, timers: list[Timer]) -> None:
        """Initialize composite timer.

        Args:
            timers: List of timer instances to delegate to
        """
        self.timers = timers

    def measure(self, name: str) -> AbstractContextManager[None]:
        """Measure using all underlying timers.

        Args:
            name: Name of the operation

        Returns:
            Context manager that manages all underlying timers
        """
        contexts = [timer.measure(name) for timer in self.timers]
        return _composite_context_manager(contexts)

    def get_metrics(self) -> dict[str, float]:
        """Get combined metrics from all timers.

        Returns:
            Merged dictionary of metrics
        """
        metrics = {}
        for timer in self.timers:
            metrics.update(timer.get_metrics())
        return metrics


class OpenTelemetryTimer:
    """Timer implementation that creates OpenTelemetry spans.

    Maps 'measure' calls to OTel spans. Requires opentelemetry-api installed.
    """

    __slots__ = ("tracer",)

    def __init__(self, tracer: Tracer | None = None) -> None:
        """Initialize OTel timer.

        Args:
            tracer: Optional OTel tracer. If None, gets tracer for module name.
        """
        if not _OPENTELEMETRY_AVAILABLE:
            self.tracer = None  # Always initialize self.tracer for __slots__
            return

        if trace is not None:
            self.tracer = tracer or trace.get_tracer(__name__)
        else:
            # This branch should ideally not be reached if _OPENTELEMETRY_AVAILABLE
            # is True but trace is None (meaning import succeeded but trace was not what
            # expected). Defensive programming: ensure self.tracer is set.
            self.tracer = None

    def measure(self, name: str) -> AbstractContextManager[None]:
        """Start an OpenTelemetry span.

        Args:
            name: Name of the span

        Returns:
            Span context manager (compatible with AbstractContextManager)
        """
        if not _OPENTELEMETRY_AVAILABLE or self.tracer is None:
            return _NULL_CONTEXT  # Return the no-op context

        return self.tracer.start_as_current_span(name)

    def get_metrics(self) -> dict[str, float]:
        """Return empty metrics (OTel handles export asynchronously).

        Returns:
            Empty dictionary
        """
        return {}
