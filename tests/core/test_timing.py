"""Tests for performance timing utilities."""

import time

from kinemotion.core.timing import (
    NULL_TIMER,
    NullTimer,
    PerformanceTimer,
    Timer,
)


def test_performance_timer_init() -> None:
    """Test timer initialization."""
    timer = PerformanceTimer()
    assert timer.metrics == {}


def test_performance_timer_measure() -> None:
    """Test measuring execution time."""
    timer = PerformanceTimer()

    with timer.measure("test_step"):
        time.sleep(0.01)

    metrics = timer.get_metrics()
    assert "test_step" in metrics
    assert metrics["test_step"] >= 0.01


def test_performance_timer_multiple_steps() -> None:
    """Test measuring multiple steps."""
    timer = PerformanceTimer()

    with timer.measure("step1"):
        pass

    with timer.measure("step2"):
        pass

    metrics = timer.get_metrics()
    assert "step1" in metrics
    assert "step2" in metrics
    assert len(metrics) == 2


def test_get_metrics_returns_copy() -> None:
    """Test that get_metrics returns a copy of the dictionary."""
    timer = PerformanceTimer()
    with timer.measure("step"):
        pass

    metrics = timer.get_metrics()
    metrics["new_key"] = 1.0

    # Original metrics should not be modified
    assert "new_key" not in timer.metrics


def test_performance_timer_accumulates_metrics() -> None:
    """Test that multiple measurements accumulate in metrics."""
    timer = PerformanceTimer()

    with timer.measure("operation_a"):
        time.sleep(0.005)

    with timer.measure("operation_b"):
        time.sleep(0.005)

    with timer.measure("operation_c"):
        pass

    metrics = timer.get_metrics()
    assert len(metrics) == 3
    assert metrics["operation_a"] >= 0.005
    assert metrics["operation_b"] >= 0.005
    assert metrics["operation_c"] >= 0.0


def test_performance_timer_accumulates_same_operation() -> None:
    """Test that repeated measurements of same operation accumulate."""
    timer = PerformanceTimer()

    # Measure same operation multiple times (e.g., in a loop)
    with timer.measure("loop_operation"):
        time.sleep(0.005)

    with timer.measure("loop_operation"):
        time.sleep(0.005)

    with timer.measure("loop_operation"):
        time.sleep(0.005)

    metrics = timer.get_metrics()
    assert len(metrics) == 1
    assert "loop_operation" in metrics
    # Total should be sum of all three measurements
    assert metrics["loop_operation"] >= 0.015


def test_null_timer_basic() -> None:
    """Test that NullTimer provides no-op functionality."""
    timer = NullTimer()

    # Should not raise any errors
    with timer.measure("operation"):
        time.sleep(0.001)

    # Should return empty metrics
    metrics = timer.get_metrics()
    assert metrics == {}


def test_null_timer_singleton() -> None:
    """Test that NULL_TIMER is a singleton instance."""
    timer = NULL_TIMER

    # Should work like NullTimer
    with timer.measure("operation"):
        time.sleep(0.001)

    assert timer.get_metrics() == {}


def test_null_timer_zero_overhead() -> None:
    """Test that NullTimer has negligible overhead."""
    null_timer = NULL_TIMER
    perf_timer = PerformanceTimer()

    # Measure with null timer (should be near instant)
    start = time.perf_counter()
    for _ in range(1000):
        with null_timer.measure("operation"):
            pass
    null_duration = time.perf_counter() - start

    # Measure with performance timer
    start = time.perf_counter()
    for _ in range(1000):
        with perf_timer.measure("operation"):
            pass
    perf_duration = time.perf_counter() - start

    # Null timer should be faster than performance timer
    assert null_duration <= perf_duration
    # Both should be reasonably fast (less than 10ms for 1000 iterations)
    assert null_duration < 0.01
    assert perf_duration < 0.01


def test_timer_protocol_conformance() -> None:
    """Test that PerformanceTimer and NullTimer conform to Timer protocol."""
    # Both should be instances of Timer protocol
    assert isinstance(PerformanceTimer(), Timer)
    assert isinstance(NullTimer(), Timer)
    assert isinstance(NULL_TIMER, Timer)


def test_performance_timer_uses_perf_counter() -> None:
    """Test that PerformanceTimer provides high precision timing."""
    timer = PerformanceTimer()

    # Measure a very short operation
    with timer.measure("short_operation"):
        # Just a few loop iterations
        for _ in range(100):
            pass

    metrics = timer.get_metrics()
    # perf_counter should detect even microsecond-level durations
    # The measurement should be non-zero and very small
    assert metrics["short_operation"] >= 0.0
    # Should be less than 1ms for 100 iterations
    assert metrics["short_operation"] < 0.001


def test_performance_timer_memory_efficiency() -> None:
    """Test that PerformanceTimer uses __slots__ for memory efficiency."""
    timer = PerformanceTimer()

    # __slots__ means no __dict__ attribute
    assert not hasattr(timer, "__dict__")

    # Should only have metrics attribute
    assert hasattr(timer, "metrics")


def test_null_timer_memory_efficiency() -> None:
    """Test that NullTimer uses __slots__ for minimal memory."""
    timer = NullTimer()

    # __slots__ means no __dict__ attribute
    assert not hasattr(timer, "__dict__")

    # NullTimer should have no instance attributes (empty __slots__)
    assert len(timer.__slots__) == 0
