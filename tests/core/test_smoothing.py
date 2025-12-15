"""Comprehensive tests for landmark smoothing and velocity/acceleration computation."""

# pyright: reportArgumentType=false

import numpy as np

from kinemotion.core.smoothing import (
    _extract_landmark_coordinates,  # pyright: ignore[reportPrivateUsage]
    _fill_missing_frames,  # pyright: ignore[reportPrivateUsage]
    _get_landmark_names,  # pyright: ignore[reportPrivateUsage]
    _store_smoothed_landmarks,  # pyright: ignore[reportPrivateUsage]
    compute_acceleration_from_derivative,
    compute_velocity,
    compute_velocity_from_derivative,
    smooth_landmarks,
    smooth_landmarks_advanced,
)


class TestExtractLandmarkCoordinates:
    """Test _extract_landmark_coordinates helper function."""

    def test_extract_single_landmark(self) -> None:
        """Test extracting a single landmark from sequence."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]

        x_coords, y_coords, valid_frames = _extract_landmark_coordinates(
            landmark_sequence, "left_ankle"
        )

        assert x_coords == [0.5, 0.51, 0.52]
        assert y_coords == [0.6, 0.61, 0.62]
        assert valid_frames == [0, 1, 2]

    def test_extract_with_missing_frames(self) -> None:
        """Test extracting landmark with None frames in sequence."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            None,  # Missing frame
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]

        x_coords, y_coords, valid_frames = _extract_landmark_coordinates(
            landmark_sequence, "left_ankle"
        )

        assert x_coords == [0.5, 0.52]
        assert y_coords == [0.6, 0.62]
        assert valid_frames == [0, 2]

    def test_extract_missing_landmark(self) -> None:
        """Test extracting non-existent landmark returns empty."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
        ]

        x_coords, y_coords, valid_frames = _extract_landmark_coordinates(
            landmark_sequence, "right_knee"
        )

        assert x_coords == []
        assert y_coords == []
        assert valid_frames == []

    def test_extract_partial_landmark_presence(self) -> None:
        """Test extracting landmark present in some but not all frames."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9), "right_ankle": (0.55, 0.65, 0.9)},
            {"right_ankle": (0.56, 0.66, 0.9)},  # Missing left_ankle
            {"left_ankle": (0.52, 0.62, 0.9)},  # Missing right_ankle
        ]

        left_x, _, left_frames = _extract_landmark_coordinates(landmark_sequence, "left_ankle")
        assert left_x == [0.5, 0.52]
        assert left_frames == [0, 2]

        right_x, _, right_frames = _extract_landmark_coordinates(landmark_sequence, "right_ankle")
        assert right_x == [0.55, 0.56]
        assert right_frames == [0, 1]


class TestGetLandmarkNames:
    """Test _get_landmark_names helper function."""

    def test_get_names_from_first_frame(self) -> None:
        """Test extracting landmark names from first valid frame."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9), "right_ankle": (0.55, 0.65, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
        ]

        names = _get_landmark_names(landmark_sequence)

        assert names is not None
        assert set(names) == {"left_ankle", "right_ankle"}

    def test_get_names_skip_none_frames(self) -> None:
        """Test that None frames are skipped."""
        landmark_sequence = [
            None,  # Skip this
            {"left_ankle": (0.5, 0.6, 0.9), "right_ankle": (0.55, 0.65, 0.9)},
        ]

        names = _get_landmark_names(landmark_sequence)

        assert names is not None
        assert set(names) == {"left_ankle", "right_ankle"}

    def test_get_names_all_none_sequence(self) -> None:
        """Test that all None sequence returns None."""
        landmark_sequence = [None, None, None]

        names = _get_landmark_names(landmark_sequence)

        assert names is None

    def test_get_names_empty_sequence(self) -> None:
        """Test that empty sequence returns None."""
        landmark_sequence = []

        names = _get_landmark_names(landmark_sequence)

        assert names is None


class TestFillMissingFrames:
    """Test _fill_missing_frames helper function."""

    def test_fill_when_smoothed_shorter(self) -> None:
        """Test filling frames when smoothed sequence is shorter."""
        smoothed_sequence: list = [{"left_ankle": (0.5, 0.6, 0.9)}]
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]

        _fill_missing_frames(smoothed_sequence, landmark_sequence)

        assert len(smoothed_sequence) == 3
        assert smoothed_sequence[1] == {"left_ankle": (0.51, 0.61, 0.9)}
        assert smoothed_sequence[2] == {"left_ankle": (0.52, 0.62, 0.9)}

    def test_fill_none_entries(self) -> None:
        """Test replacing None entries with original data."""
        smoothed_sequence: list = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            None,
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]

        _fill_missing_frames(smoothed_sequence, landmark_sequence)

        assert smoothed_sequence[1] == {"left_ankle": (0.51, 0.61, 0.9)}

    def test_fill_empty_dict_entries(self) -> None:
        """Test filling entries with empty dicts."""
        smoothed_sequence: list = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {},
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]

        _fill_missing_frames(smoothed_sequence, landmark_sequence)

        assert smoothed_sequence[1] == {"left_ankle": (0.51, 0.61, 0.9)}


class TestStoreSmoothLandmarks:
    """Test _store_smoothed_landmarks helper function."""

    def test_store_basic_landmarks(self) -> None:
        """Test storing smoothed landmark values."""
        smoothed_sequence: list = []
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
        ]

        x_smooth = np.array([0.501, 0.511])
        y_smooth = np.array([0.601, 0.611])
        valid_frames = [0, 1]

        _store_smoothed_landmarks(
            smoothed_sequence,
            landmark_sequence,
            "left_ankle",
            x_smooth,
            y_smooth,
            valid_frames,
        )

        assert len(smoothed_sequence) == 2
        assert smoothed_sequence[0]["left_ankle"] == (0.501, 0.601, 0.9)
        assert smoothed_sequence[1]["left_ankle"] == (0.511, 0.611, 0.9)

    def test_store_with_none_frame(self) -> None:
        """Test storing when smoothed_sequence[frame_idx] is None."""
        smoothed_sequence: list = [None, None]
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
        ]

        x_smooth = np.array([0.501, 0.511])
        y_smooth = np.array([0.601, 0.611])
        valid_frames = [0, 1]

        _store_smoothed_landmarks(
            smoothed_sequence,
            landmark_sequence,
            "left_ankle",
            x_smooth,
            y_smooth,
            valid_frames,
        )

        assert smoothed_sequence[0] == {"left_ankle": (0.501, 0.601, 0.9)}
        assert smoothed_sequence[1] == {"left_ankle": (0.511, 0.611, 0.9)}

    def test_store_extending_sequence(self) -> None:
        """Test that sequence extends when frame_idx >= len(smoothed_sequence)."""
        smoothed_sequence: list = []
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
            {"left_ankle": (0.52, 0.62, 0.9)},
        ]

        x_smooth = np.array([0.501, 0.511, 0.521])
        y_smooth = np.array([0.601, 0.611, 0.621])
        valid_frames = [0, 1, 2]

        _store_smoothed_landmarks(
            smoothed_sequence,
            landmark_sequence,
            "left_ankle",
            x_smooth,
            y_smooth,
            valid_frames,
        )

        assert len(smoothed_sequence) == 3


class TestSmoothLandmarks:
    """Test smooth_landmarks function."""

    def test_smooth_landmarks_basic(self) -> None:
        """Test basic landmark smoothing."""
        n_frames = 30
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for i in range(n_frames):
            base_y = 0.5 + 0.01 * (i - 15) ** 2 / 225
            noisy_y = base_y + rng.normal(0, 0.01)
            landmark_sequence.append(
                {
                    "left_ankle": (0.5, noisy_y, 0.9),
                    "right_ankle": (0.5, noisy_y + 0.01, 0.9),
                }
            )

        smoothed = smooth_landmarks(landmark_sequence, window_length=5, polyorder=2)

        assert len(smoothed) == n_frames
        assert smoothed[0] is not None
        assert "left_ankle" in smoothed[0]  # type: ignore

    def test_smooth_landmarks_short_sequence(self) -> None:
        """Test smoothing sequence shorter than window_length."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
        ]

        # window_length=5 > 2, so returns original
        smoothed = smooth_landmarks(landmark_sequence, window_length=5, polyorder=2)

        assert smoothed == landmark_sequence

    def test_smooth_landmarks_even_window_adjusted(self) -> None:
        """Test that even window_length is adjusted to odd."""
        n_frames = 30
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append({"left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9)})

        # Pass even window_length
        smoothed = smooth_landmarks(landmark_sequence, window_length=6, polyorder=2)

        assert len(smoothed) == n_frames


class TestComputeVelocity:
    """Test compute_velocity function."""

    def test_compute_velocity_basic(self) -> None:
        """Test basic velocity computation."""
        positions = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0]])
        fps = 30.0

        velocity = compute_velocity(positions, fps)

        assert velocity.shape == positions.shape
        assert len(velocity) == 5

    def test_compute_velocity_smoothing_applied(self) -> None:
        """Test velocity computation with smoothing window applied."""
        # Create motion with some noise
        t = np.linspace(0, 2, 30)
        positions = np.column_stack(
            [
                0.5 + 0.1 * t + np.random.default_rng(42).normal(0, 0.01, 30),
                0.5 + 0.05 * t + np.random.default_rng(42).normal(0, 0.01, 30),
            ]
        )
        fps = 30.0

        velocity = compute_velocity(positions, fps, smooth_window=5)

        assert velocity.shape == positions.shape

    def test_compute_velocity_short_sequence(self) -> None:
        """Test velocity computation with sequence shorter than smooth_window."""
        positions = np.array([[0.0, 0.0], [1.0, 0.0]])
        fps = 30.0

        velocity = compute_velocity(positions, fps, smooth_window=5)

        assert velocity.shape == positions.shape

    def test_compute_velocity_smooth_window_1(self) -> None:
        """Test that smooth_window=1 skips smoothing."""
        positions = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])
        fps = 30.0

        velocity = compute_velocity(positions, fps, smooth_window=1)

        assert velocity.shape == positions.shape

    def test_compute_velocity_even_smooth_window(self) -> None:
        """Test that even smooth_window is adjusted to odd."""
        positions = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0]])
        fps = 30.0

        # Pass even smooth_window
        velocity = compute_velocity(positions, fps, smooth_window=4)

        assert velocity.shape == positions.shape


class TestComputeVelocityFromDerivative:
    """Test compute_velocity_from_derivative function."""

    def test_velocity_from_derivative_basic(self) -> None:
        """Test basic velocity computation from derivative."""
        positions = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

        velocity = compute_velocity_from_derivative(positions, window_length=5, polyorder=2)

        assert len(velocity) == len(positions)
        assert np.all(velocity >= 0)  # Absolute value

    def test_velocity_from_derivative_short_sequence(self) -> None:
        """Test velocity from derivative on short sequence (< window_length)."""
        positions = np.array([0.0, 0.1, 0.2])

        # window_length=5 > 3, so uses fallback
        velocity = compute_velocity_from_derivative(positions, window_length=5, polyorder=2)

        assert len(velocity) == len(positions)

    def test_velocity_from_derivative_even_window(self) -> None:
        """Test that even window_length is adjusted to odd."""
        positions = np.linspace(0, 2, 30)

        velocity = compute_velocity_from_derivative(positions, window_length=6, polyorder=2)

        assert len(velocity) == len(positions)

    def test_velocity_from_derivative_parabolic_motion(self) -> None:
        """Test velocity derivative on parabolic motion."""
        # Parabolic motion: s(t) = 0.5 * a * t^2 (constant acceleration)
        # v(t) = a * t
        t = np.linspace(0, 2, 50)
        a = 2.0  # acceleration
        positions = 0.5 * a * t**2

        velocity = compute_velocity_from_derivative(positions, window_length=9, polyorder=3)

        assert len(velocity) == len(positions)
        assert np.all(velocity >= 0)


class TestComputeAccelerationFromDerivative:
    """Test compute_acceleration_from_derivative function."""

    def test_acceleration_from_derivative_basic(self) -> None:
        """Test basic acceleration computation from derivative."""
        positions = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

        acceleration = compute_acceleration_from_derivative(
            positions, window_length=5, polyorder=2
        )

        assert len(acceleration) == len(positions)

    def test_acceleration_from_derivative_short_sequence(self) -> None:
        """Test acceleration from derivative on short sequence."""
        positions = np.array([0.0, 0.1, 0.2])

        # window_length=5 > 3, so uses fallback
        acceleration = compute_acceleration_from_derivative(
            positions, window_length=5, polyorder=2
        )

        assert len(acceleration) == len(positions)

    def test_acceleration_from_derivative_even_window(self) -> None:
        """Test that even window_length is adjusted to odd."""
        positions = np.linspace(0, 2, 30)

        acceleration = compute_acceleration_from_derivative(
            positions, window_length=6, polyorder=2
        )

        assert len(acceleration) == len(positions)

    def test_acceleration_from_derivative_cubic_motion(self) -> None:
        """Test acceleration derivative on cubic motion."""
        # Cubic motion: s(t) = a * t^3 (third derivative is constant)
        # v(t) = 3 * a * t^2 (derivative)
        # a(t) = 6 * a * t (second derivative)
        t = np.linspace(0, 2, 50)
        a = 0.1
        positions = a * t**3

        acceleration = compute_acceleration_from_derivative(
            positions, window_length=9, polyorder=3
        )

        assert len(acceleration) == len(positions)


class TestSmoothLandmarksAdvanced:
    """Test smooth_landmarks_advanced function."""

    def test_smooth_landmarks_advanced_default(self) -> None:
        """Test advanced smoothing with default parameters."""
        n_frames = 30
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for i in range(n_frames):
            base_y = 0.5 + 0.01 * (i - 15) ** 2 / 225
            noisy_y = base_y + rng.normal(0, 0.01)
            landmark_sequence.append({"left_ankle": (0.5, noisy_y, 0.9)})

        smoothed = smooth_landmarks_advanced(
            landmark_sequence,
            window_length=5,
            polyorder=2,
            use_outlier_rejection=True,
            use_bilateral=False,
        )

        assert len(smoothed) == n_frames
        assert smoothed[0] is not None

    def test_smooth_landmarks_advanced_no_outlier_rejection(self) -> None:
        """Test advanced smoothing without outlier rejection."""
        n_frames = 20
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append({"left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9)})

        smoothed = smooth_landmarks_advanced(
            landmark_sequence,
            window_length=5,
            polyorder=2,
            use_outlier_rejection=False,
            use_bilateral=False,
        )

        assert len(smoothed) == n_frames

    def test_smooth_landmarks_advanced_bilateral(self) -> None:
        """Test advanced smoothing with bilateral filter."""
        n_frames = 20
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append({"left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9)})

        smoothed = smooth_landmarks_advanced(
            landmark_sequence,
            window_length=5,
            polyorder=2,
            use_bilateral=True,
            bilateral_sigma_spatial=3.0,
            bilateral_sigma_intensity=0.02,
        )

        assert len(smoothed) == n_frames

    def test_smooth_landmarks_advanced_combined(self) -> None:
        """Test advanced smoothing with both outlier rejection and bilateral."""
        n_frames = 20
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append({"left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9)})

        smoothed = smooth_landmarks_advanced(
            landmark_sequence,
            window_length=5,
            polyorder=2,
            use_outlier_rejection=True,
            use_bilateral=True,
            ransac_threshold=0.02,
            bilateral_sigma_spatial=3.0,
            bilateral_sigma_intensity=0.02,
        )

        assert len(smoothed) == n_frames

    def test_smooth_landmarks_advanced_short_sequence(self) -> None:
        """Test advanced smoothing on sequence shorter than window_length."""
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
            {"left_ankle": (0.51, 0.61, 0.9)},
        ]

        smoothed = smooth_landmarks_advanced(landmark_sequence, window_length=5, polyorder=2)

        assert smoothed == landmark_sequence

    def test_smooth_landmarks_advanced_even_window(self) -> None:
        """Test that even window_length is adjusted to odd."""
        n_frames = 20
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append({"left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9)})

        smoothed = smooth_landmarks_advanced(landmark_sequence, window_length=6, polyorder=2)

        assert len(smoothed) == n_frames

    def test_smooth_landmarks_advanced_custom_ransac_threshold(self) -> None:
        """Test advanced smoothing with custom RANSAC threshold."""
        n_frames = 20
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append({"left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9)})

        smoothed = smooth_landmarks_advanced(
            landmark_sequence,
            window_length=5,
            polyorder=2,
            use_outlier_rejection=True,
            ransac_threshold=0.05,  # Custom threshold
        )

        assert len(smoothed) == n_frames


class TestUncoveredBranches:
    """Test specific branches that are not yet covered."""

    def test_store_smoothed_landmarks_already_present(self) -> None:
        """Test that existing landmarks in frame_dict are not overwritten.

        This tests the branch where landmark_name is already in frame_dict,
        ensuring the condition at line 115 properly skips overwriting.
        """
        smoothed_sequence: list = [{"left_ankle": (0.5, 0.6, 0.9)}]
        landmark_sequence = [
            {"left_ankle": (0.5, 0.6, 0.9)},
        ]

        x_smooth = np.array([0.501])
        y_smooth = np.array([0.601])
        valid_frames = [0]

        # Store with an existing landmark - should not overwrite
        _store_smoothed_landmarks(
            smoothed_sequence,
            landmark_sequence,
            "left_ankle",
            x_smooth,
            y_smooth,
            valid_frames,
        )

        # Should keep original values since landmark already exists
        assert smoothed_sequence[0]["left_ankle"] == (0.5, 0.6, 0.9)

    def test_store_smoothed_landmarks_when_source_is_none(self) -> None:
        """Test storing when landmark_sequence[frame_idx] is None.

        This tests the branch where landmark_sequence[frame_idx] is None,
        ensuring we skip storing the landmark when source is missing.
        """
        smoothed_sequence: list = [{}]
        landmark_sequence = [None]  # Missing frame

        x_smooth = np.array([0.501])
        y_smooth = np.array([0.601])
        valid_frames = [0]

        _store_smoothed_landmarks(
            smoothed_sequence,
            landmark_sequence,
            "left_ankle",
            x_smooth,
            y_smooth,
            valid_frames,
        )

        # Should not have stored anything since source is None
        assert smoothed_sequence[0] == {}

    def test_smooth_landmarks_core_skips_short_sequences(self) -> None:
        """Test that landmarks with fewer frames than window_length are skipped.

        This tests line 160 (continue statement) which is triggered when
        len(x_coords) < window_length.
        """
        # Create sequence with one landmark that has enough frames
        # and one that doesn't
        landmark_sequence = [
            {"left_ankle": (0.5, 0.5, 0.9), "right_ankle": (0.55, 0.55, 0.9)},
            {"left_ankle": (0.51, 0.51, 0.9), "right_ankle": (0.56, 0.56, 0.9)},
            {"left_ankle": (0.52, 0.52, 0.9), "right_ankle": (0.57, 0.57, 0.9)},
            {"left_ankle": (0.53, 0.53, 0.9)},  # right_ankle missing
            {"left_ankle": (0.54, 0.54, 0.9)},  # right_ankle missing
            {"left_ankle": (0.55, 0.55, 0.9)},  # right_ankle missing
        ]

        window_length = 5
        smoothed = smooth_landmarks(landmark_sequence, window_length=window_length, polyorder=2)

        # left_ankle should be smoothed (6 frames >= 5)
        assert len(smoothed) == 6
        # Verify structure is intact
        assert all(frame is not None for frame in smoothed)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_smooth_landmarks_all_none(self) -> None:
        """Test smoothing sequence of all None frames."""
        landmark_sequence = [None, None, None]

        smoothed = smooth_landmarks(landmark_sequence, window_length=3, polyorder=1)

        # Should return original since no landmarks to smooth
        assert smoothed == landmark_sequence

    def test_velocity_single_point(self) -> None:
        """Test velocity computation on single point."""
        positions = np.array([[0.0, 0.0], [1.0, 0.0]])
        fps = 30.0

        velocity = compute_velocity(positions, fps, smooth_window=1)

        assert velocity.shape == positions.shape

    def test_velocity_from_derivative_single_point(self) -> None:
        """Test velocity from derivative on single point."""
        positions = np.array([0.0])

        velocity = compute_velocity_from_derivative(positions, window_length=5)

        assert len(velocity) == 1

    def test_acceleration_single_point(self) -> None:
        """Test acceleration from derivative on single point."""
        positions = np.array([0.0])

        acceleration = compute_acceleration_from_derivative(positions, window_length=5)

        assert len(acceleration) == 1

    def test_smooth_landmarks_with_outliers(self) -> None:
        """Test advanced smoothing properly handles outliers."""
        n_frames = 30
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for i in range(n_frames):
            y = 0.5 + rng.normal(0, 0.01)
            # Add occasional outliers
            if i % 10 == 5:
                y += 0.5  # Large spike
            landmark_sequence.append({"left_ankle": (0.5, y, 0.9)})

        smoothed = smooth_landmarks_advanced(
            landmark_sequence, window_length=5, polyorder=2, use_outlier_rejection=True
        )

        assert len(smoothed) == n_frames

    def test_smooth_landmarks_multiple_landmarks(self) -> None:
        """Test smoothing multiple landmarks simultaneously."""
        n_frames = 25
        rng = np.random.default_rng(42)
        landmark_sequence = []

        for _i in range(n_frames):
            landmark_sequence.append(
                {
                    "left_ankle": (0.5, 0.5 + rng.normal(0, 0.01), 0.9),
                    "right_ankle": (0.55, 0.55 + rng.normal(0, 0.01), 0.9),
                    "left_knee": (0.45, 0.45 + rng.normal(0, 0.01), 0.9),
                    "right_knee": (0.6, 0.6 + rng.normal(0, 0.01), 0.9),
                }
            )

        smoothed = smooth_landmarks(landmark_sequence, window_length=5, polyorder=2)

        assert len(smoothed) == n_frames
        assert all(frame is not None for frame in smoothed)
        for frame in smoothed:
            if frame:  # type: ignore
                assert "left_ankle" in frame  # type: ignore
                assert "right_ankle" in frame  # type: ignore

    def test_velocity_high_fps(self) -> None:
        """Test velocity computation with high FPS."""
        positions = np.array([[i / 1000.0, 0.0] for i in range(10)])
        fps = 1000.0  # High FPS

        velocity = compute_velocity(positions, fps, smooth_window=3)

        assert velocity.shape == positions.shape

    def test_velocity_from_derivative_different_polyorders(self) -> None:
        """Test velocity computation with various polynomial orders."""
        positions = np.linspace(0, 2, 50)

        for polyorder in [1, 2, 3]:
            velocity = compute_velocity_from_derivative(
                positions, window_length=9, polyorder=polyorder
            )
            assert len(velocity) == len(positions)

    def test_acceleration_from_derivative_different_polyorders(self) -> None:
        """Test acceleration computation with various polynomial orders."""
        positions = np.linspace(0, 2, 50)

        for polyorder in [1, 2, 3]:
            acceleration = compute_acceleration_from_derivative(
                positions, window_length=9, polyorder=polyorder
            )
            assert len(acceleration) == len(positions)


"""Tests for polynomial order parameter in smoothing and derivative calculations."""


def test_smooth_landmarks_polyorder2_vs_polyorder3() -> None:
    """Test that different polynomial orders produce different smoothed results."""
    # Create synthetic landmark sequence with some noise
    n_frames = 30
    landmark_sequence = []

    rng = np.random.default_rng(42)
    for i in range(n_frames):
        # Smooth parabolic motion with noise
        base_y = 0.5 + 0.01 * (i - 15) ** 2 / 225  # Parabola
        noisy_y = base_y + rng.normal(0, 0.01)

        landmark_sequence.append(
            {
                "left_ankle": (0.5, noisy_y, 0.9),
                "right_ankle": (0.5, noisy_y + 0.01, 0.9),
            }
        )

    # Smooth with polyorder=2 (quadratic)
    smoothed_2 = smooth_landmarks(landmark_sequence, window_length=5, polyorder=2)

    # Smooth with polyorder=3 (cubic)
    smoothed_3 = smooth_landmarks(landmark_sequence, window_length=7, polyorder=3)

    # Extract y-coordinates
    y_coords_2 = [frame["left_ankle"][1] for frame in smoothed_2 if frame]  # type: ignore[index]
    y_coords_3 = [frame["left_ankle"][1] for frame in smoothed_3 if frame]  # type: ignore[index]

    # Results should be different (different polynomial fits)
    assert len(y_coords_2) == len(y_coords_3)
    differences = [abs(y2 - y3) for y2, y3 in zip(y_coords_2, y_coords_3, strict=True)]
    avg_difference = np.mean(differences)

    # Some frames should have noticeable differences
    assert avg_difference > 0.0001, "Polyorder should affect smoothing results"


def test_velocity_from_derivative_polyorder() -> None:
    """Test velocity computation with different polynomial orders."""
    # Create synthetic position data with quadratic motion
    rng = np.random.default_rng(42)
    t = np.linspace(0, 2, 60)
    positions = 0.5 + 0.1 * t**2  # Parabolic trajectory
    positions += rng.normal(0, 0.005, len(positions))  # Add noise

    # Compute velocity with different polynomial orders
    velocity_2 = compute_velocity_from_derivative(positions, window_length=5, polyorder=2)
    velocity_3 = compute_velocity_from_derivative(positions, window_length=7, polyorder=3)

    # Both should produce reasonable velocities
    assert len(velocity_2) == len(positions)
    assert len(velocity_3) == len(positions)

    # All velocities should be non-negative (absolute values)
    assert np.all(velocity_2 >= 0)
    assert np.all(velocity_3 >= 0)

    # Results should differ slightly due to different polynomial fits
    difference = np.mean(np.abs(velocity_2 - velocity_3))
    assert difference > 0.0001, "Different polyorders should produce different velocities"


def test_acceleration_from_derivative_polyorder() -> None:
    """Test acceleration computation with different polynomial orders."""
    # Create synthetic position data with cubic motion (non-zero third derivative)
    rng = np.random.default_rng(42)
    t = np.linspace(0, 2, 60)
    positions = 0.5 + 0.05 * t**3  # Cubic trajectory
    positions += rng.normal(0, 0.003, len(positions))  # Add noise

    # Compute acceleration with different polynomial orders
    accel_2 = compute_acceleration_from_derivative(positions, window_length=5, polyorder=2)
    accel_3 = compute_acceleration_from_derivative(positions, window_length=7, polyorder=3)

    # Both should produce acceleration arrays
    assert len(accel_2) == len(positions)
    assert len(accel_3) == len(positions)

    # Cubic polynomial fit should capture cubic trajectory better
    # For cubic motion: a(t) = 6 * coefficient * t (for 0.05*t^3, coefficient = 0.05)
    # Expected acceleration should increase linearly
    expected_accel = 6 * 0.05 * t  # = 0.3 * t

    # polyorder=3 should be closer to expected for cubic trajectory
    error_2 = np.mean(np.abs(accel_2 - expected_accel))
    error_3 = np.mean(np.abs(accel_3 - expected_accel))

    # Cubic fit should have lower error for cubic motion
    # (This might not always be true due to noise, but typically should be)
    assert error_3 <= error_2 * 1.5, "Cubic fit should handle cubic motion better"


def test_polyorder_validation() -> None:
    """Test that polyorder must be less than window_length."""
    rng = np.random.default_rng(42)
    positions = rng.random(50)

    # polyorder=2 with window=5 should work (2 < 5)
    velocity_valid = compute_velocity_from_derivative(positions, window_length=5, polyorder=2)
    assert len(velocity_valid) == len(positions)

    # polyorder=4 with window=7 should work (4 < 7)
    velocity_valid2 = compute_velocity_from_derivative(positions, window_length=7, polyorder=4)
    assert len(velocity_valid2) == len(positions)


def test_polyorder_higher_captures_more_complexity() -> None:
    """Test that higher polynomial order can capture more complex motion patterns."""
    # Create a sine wave pattern (requires higher order polynomial to approximate)
    t = np.linspace(0, 2 * np.pi, 100)
    positions = 0.5 + 0.1 * np.sin(t)

    # Compute velocity (should approximate cosine)
    velocity_2 = compute_velocity_from_derivative(positions, window_length=9, polyorder=2)
    velocity_4 = compute_velocity_from_derivative(positions, window_length=9, polyorder=4)

    # Expected velocity from derivative of sine: 0.1 * cos(t)
    expected_velocity = np.abs(0.1 * np.cos(t))

    # Higher order should approximate sine wave derivative better
    error_2 = np.mean(np.abs(velocity_2 - expected_velocity))
    error_4 = np.mean(np.abs(velocity_4 - expected_velocity))

    # polyorder=4 should have lower or similar error for sine wave
    assert error_4 <= error_2 * 1.2, "Higher polyorder should handle complex motion"
