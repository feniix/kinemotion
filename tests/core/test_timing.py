"""Tests for performance timing utilities."""

import time

from kinemotion.core.timing import PerformanceTimer


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
