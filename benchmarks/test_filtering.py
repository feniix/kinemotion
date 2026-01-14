"""Performance benchmarks for filtering functions.

Tests the vectorized implementations of:
- bilateral_temporal_filter
- detect_outliers_ransac
"""

import numpy as np
import pytest

from kinemotion.core.filtering import (
    bilateral_temporal_filter,
    detect_outliers_median,
    detect_outliers_ransac,
)


def _generate_jump_trajectory(n_frames: int) -> np.ndarray:
    """Generate realistic jump trajectory for benchmarking.

    Simulates a CMJ with: standing → countermovement → jump → flight → landing
    """
    t = np.linspace(0, n_frames / 30, n_frames)  # Assume 30 fps

    # Base trajectory: start high, squat down, jump up, land
    base = 0.5 + 0.15 * np.sin(2 * np.pi * t / 2)

    # Add realistic noise (MediaPipe tracking jitter)
    noise = 0.01 * np.random.randn(n_frames)

    return base + noise


@pytest.mark.benchmark
class TestBilateralTemporalFilter:
    """Benchmarks for bilateral_temporal_filter."""

    def test_small_30_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 30 frames (~1 second at 30fps)."""
        data = _generate_jump_trajectory(30)
        result = benchmark(bilateral_temporal_filter, data, window_size=9)
        assert len(result) == 30

    def test_medium_90_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 90 frames (~3 seconds at 30fps)."""
        data = _generate_jump_trajectory(90)
        result = benchmark(bilateral_temporal_filter, data, window_size=9)
        assert len(result) == 90

    def test_large_300_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 300 frames (~10 seconds at 30fps)."""
        data = _generate_jump_trajectory(300)
        result = benchmark(bilateral_temporal_filter, data, window_size=9)
        assert len(result) == 300

    def test_xlarge_600_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 600 frames (~20 seconds at 30fps)."""
        data = _generate_jump_trajectory(600)
        result = benchmark(bilateral_temporal_filter, data, window_size=9)
        assert len(result) == 600

    def test_different_window_size(self, benchmark: pytest.fixture) -> None:
        """Benchmark with larger window size."""
        data = _generate_jump_trajectory(90)
        result = benchmark(bilateral_temporal_filter, data, window_size=15)
        assert len(result) == 90


@pytest.mark.benchmark
class TestDetectOutliersRansac:
    """Benchmarks for detect_outliers_ransac."""

    def test_small_clean_data(self, benchmark: pytest.fixture) -> None:
        """Benchmark with small clean dataset."""
        data = _generate_jump_trajectory(30)
        result = benchmark(detect_outliers_ransac, data, window_size=15)
        assert len(result) == 30

    def test_medium_clean_data(self, benchmark: pytest.fixture) -> None:
        """Benchmark with medium clean dataset."""
        data = _generate_jump_trajectory(90)
        result = benchmark(detect_outliers_ransac, data, window_size=15)
        assert len(result) == 90

    def test_large_clean_data(self, benchmark: pytest.fixture) -> None:
        """Benchmark with large clean dataset."""
        data = _generate_jump_trajectory(300)
        result = benchmark(detect_outliers_ransac, data, window_size=15)
        assert len(result) == 300

    def test_medium_with_outliers(self, benchmark: pytest.fixture) -> None:
        """Benchmark with data containing outliers."""
        data = _generate_jump_trajectory(90)
        # Inject some glitches at random positions
        glitch_indices = np.random.choice(90, 5, replace=False)
        data[glitch_indices] += 0.1  # Significant jump
        result = benchmark(detect_outliers_ransac, data, window_size=15)
        assert len(result) == 90

    def test_different_window_size(self, benchmark: pytest.fixture) -> None:
        """Benchmark with different window size."""
        data = _generate_jump_trajectory(90)
        result = benchmark(detect_outliers_ransac, data, window_size=9)
        assert len(result) == 90


@pytest.mark.benchmark
class TestDetectOutliersMedian:
    """Benchmarks for detect_outliers_median."""

    def test_medium_clean_data(self, benchmark: pytest.fixture) -> None:
        """Benchmark with medium dataset."""
        data = _generate_jump_trajectory(90)
        result = benchmark(detect_outliers_median, data, window_size=5)
        assert len(result) == 90


@pytest.mark.benchmark
class TestFilteringCombined:
    """Benchmarks for combined filtering operations."""

    def test_full_outlier_pipeline(self, benchmark: pytest.fixture) -> None:
        """Benchmark full outlier detection pipeline (RANSAC + median)."""
        data = _generate_jump_trajectory(90)

        def pipeline(x: np.ndarray) -> np.ndarray:
            ransac_outliers = detect_outliers_ransac(x, window_size=15)
            median_outliers = detect_outliers_median(x, window_size=5)
            return ransac_outliers | median_outliers

        result = benchmark(pipeline, data)
        assert len(result) == 90

    def test_smoothing_with_outlier_detection(self, benchmark: pytest.fixture) -> None:
        """Benchmark smoothing after outlier detection."""
        data = _generate_jump_trajectory(90)

        def pipeline(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
            outliers = detect_outliers_ransac(x, window_size=15)
            smoothed = bilateral_temporal_filter(x, window_size=9)
            return smoothed, outliers

        smoothed, outliers = benchmark(pipeline, data)
        assert len(smoothed) == 90
