"""Tests for OpenTelemetry and Composite timer implementations."""

from unittest.mock import MagicMock, patch

import pytest

from kinemotion.core.timing import (
    CompositeTimer,
    OpenTelemetryTimer,
    PerformanceTimer,
)


@pytest.fixture
def mock_otel():
    """Mock opentelemetry module."""
    with patch("kinemotion.core.timing._OPENTELEMETRY_AVAILABLE", True):
        with patch("kinemotion.core.timing.trace") as mock_trace:
            mock_tracer = MagicMock()
            mock_span = MagicMock()
            mock_tracer.start_as_current_span.return_value = mock_span
            mock_trace.get_tracer.return_value = mock_tracer
            yield mock_tracer, mock_span


def test_composite_timer_delegation():
    """Test that CompositeTimer delegates to all underlying timers."""
    timer1 = PerformanceTimer()
    timer2 = PerformanceTimer()
    composite = CompositeTimer([timer1, timer2])

    with composite.measure("test_op"):
        pass

    assert "test_op" in timer1.get_metrics()
    assert "test_op" in timer2.get_metrics()
    assert composite.get_metrics()["test_op"] > 0
    assert timer1.get_metrics()["test_op"] > 0


def test_otel_timer_initialization(mock_otel):
    """Test OpenTelemetryTimer initialization."""
    mock_tracer, _ = mock_otel

    # Init without explicit tracer
    timer = OpenTelemetryTimer()
    assert timer.tracer == mock_tracer

    # Init with explicit tracer
    explicit_tracer = MagicMock()
    timer_explicit = OpenTelemetryTimer(tracer=explicit_tracer)
    assert timer_explicit.tracer == explicit_tracer


def test_otel_timer_measure(mock_otel):
    """Test that measure() starts an OTel span."""
    mock_tracer, mock_span = mock_otel
    timer = OpenTelemetryTimer()

    with timer.measure("test_span"):
        pass

    mock_tracer.start_as_current_span.assert_called_once_with("test_span")
    mock_span.__enter__.assert_called_once()
    mock_span.__exit__.assert_called_once()


def test_composite_timer_with_otel(mock_otel):
    """Test CompositeTimer combining PerformanceTimer and OpenTelemetryTimer."""
    mock_tracer, mock_span = mock_otel

    perf_timer = PerformanceTimer()
    otel_timer = OpenTelemetryTimer()
    composite = CompositeTimer([perf_timer, otel_timer])

    with composite.measure("hybrid_op"):
        pass

    # Verify PerformanceTimer recorded metric
    assert "hybrid_op" in perf_timer.get_metrics()

    # Verify OTel span was created
    mock_tracer.start_as_current_span.assert_called_once_with("hybrid_op")


def test_otel_fallback_when_missing():
    """Test behavior when opentelemetry is not installed."""
    with patch("kinemotion.core.timing._OPENTELEMETRY_AVAILABLE", False):
        timer = OpenTelemetryTimer()

        # Should not raise error
        with timer.measure("test"):
            pass

        assert timer.get_metrics() == {}
