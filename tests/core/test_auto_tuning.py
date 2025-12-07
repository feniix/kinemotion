"""Tests for automatic parameter tuning based on video characteristics."""

import pytest

from kinemotion.core.auto_tuning import (
    AnalysisParameters,
    QualityPreset,
    VideoCharacteristics,
    analyze_tracking_quality,
    auto_tune_parameters,
)

pytestmark = [pytest.mark.unit, pytest.mark.core]


# ===== QualityPreset Tests =====


def test_quality_preset_enum_values() -> None:
    """Test QualityPreset enum has expected values."""
    assert QualityPreset.FAST.value == "fast"
    assert QualityPreset.BALANCED.value == "balanced"
    assert QualityPreset.ACCURATE.value == "accurate"


def test_quality_preset_string_comparison() -> None:
    """Test QualityPreset can be compared to strings."""
    assert QualityPreset.FAST == "fast"
    assert QualityPreset.BALANCED == "balanced"
    assert QualityPreset.ACCURATE == "accurate"


# ===== VideoCharacteristics Tests =====


def test_video_characteristics_creation() -> None:
    """Test VideoCharacteristics dataclass creation."""
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.85,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="high",
    )

    assert chars.fps == 30.0
    assert chars.frame_count == 300
    assert chars.avg_visibility == 0.85
    assert chars.position_variance == 0.01
    assert chars.has_stable_period is True
    assert chars.tracking_quality == "high"


# ===== AnalysisParameters Tests =====


def test_analysis_parameters_creation() -> None:
    """Test AnalysisParameters dataclass creation."""
    params = AnalysisParameters(
        smoothing_window=5,
        polyorder=2,
        velocity_threshold=0.02,
        min_contact_frames=3,
        visibility_threshold=0.5,
        detection_confidence=0.5,
        tracking_confidence=0.5,
        outlier_rejection=True,
        bilateral_filter=False,
        use_curvature=True,
    )

    assert params.smoothing_window == 5
    assert params.polyorder == 2
    assert params.velocity_threshold == 0.02
    assert params.min_contact_frames == 3
    assert params.visibility_threshold == 0.5
    assert params.detection_confidence == 0.5
    assert params.tracking_confidence == 0.5
    assert params.outlier_rejection is True
    assert params.bilateral_filter is False
    assert params.use_curvature is True


def test_analysis_parameters_to_dict() -> None:
    """Test AnalysisParameters.to_dict() conversion."""
    params = AnalysisParameters(
        smoothing_window=7,
        polyorder=3,
        velocity_threshold=0.015,
        min_contact_frames=5,
        visibility_threshold=0.6,
        detection_confidence=0.7,
        tracking_confidence=0.6,
        outlier_rejection=True,
        bilateral_filter=True,
        use_curvature=True,
    )

    result = params.to_dict()

    assert isinstance(result, dict)
    assert result["smoothing_window"] == 7
    assert result["polyorder"] == 3
    assert result["velocity_threshold"] == 0.015
    assert result["min_contact_frames"] == 5
    assert result["visibility_threshold"] == 0.6
    assert result["detection_confidence"] == 0.7
    assert result["tracking_confidence"] == 0.6
    assert result["outlier_rejection"] is True
    assert result["bilateral_filter"] is True
    assert result["use_curvature"] is True


# ===== analyze_tracking_quality Tests =====


def test_analyze_tracking_quality_low() -> None:
    """Test tracking quality classification for low visibility."""
    assert analyze_tracking_quality(0.1) == "low"
    assert analyze_tracking_quality(0.3) == "low"
    assert analyze_tracking_quality(0.39) == "low"


def test_analyze_tracking_quality_medium() -> None:
    """Test tracking quality classification for medium visibility."""
    assert analyze_tracking_quality(0.4) == "medium"
    assert analyze_tracking_quality(0.5) == "medium"
    assert analyze_tracking_quality(0.69) == "medium"


def test_analyze_tracking_quality_high() -> None:
    """Test tracking quality classification for high visibility."""
    assert analyze_tracking_quality(0.7) == "high"
    assert analyze_tracking_quality(0.85) == "high"
    assert analyze_tracking_quality(0.99) == "high"


def test_analyze_tracking_quality_boundary_values() -> None:
    """Test tracking quality at exact boundary values."""
    assert analyze_tracking_quality(0.4) == "medium"  # Exactly at low/medium boundary
    assert analyze_tracking_quality(0.7) == "high"  # Exactly at medium/high boundary


# ===== auto_tune_parameters Tests =====


def test_auto_tune_parameters_high_quality_video() -> None:
    """Test auto_tune_parameters with high quality video characteristics."""
    chars = VideoCharacteristics(
        fps=60.0,
        frame_count=600,
        avg_visibility=0.9,
        position_variance=0.005,
        has_stable_period=True,
        tracking_quality="high",
    )

    params = auto_tune_parameters(chars, QualityPreset.BALANCED)

    assert isinstance(params, AnalysisParameters)
    assert params.smoothing_window > 0
    assert params.polyorder >= 2
    assert params.velocity_threshold > 0
    assert params.visibility_threshold > 0
    assert params.detection_confidence > 0
    assert params.tracking_confidence > 0


def test_auto_tune_parameters_low_quality_video() -> None:
    """Test auto_tune_parameters with low quality video characteristics."""
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.3,
        position_variance=0.05,
        has_stable_period=False,
        tracking_quality="low",
    )

    params = auto_tune_parameters(chars, QualityPreset.FAST)

    assert isinstance(params, AnalysisParameters)
    # Low quality should result in different tuning
    assert params.visibility_threshold <= 0.5  # Lower threshold for low visibility


def test_auto_tune_parameters_fast_preset() -> None:
    """Test auto_tune_parameters with fast quality preset."""
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.7,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="medium",
    )

    params = auto_tune_parameters(chars, QualityPreset.FAST)

    # Fast preset should produce valid parameters
    assert isinstance(params, AnalysisParameters)
    assert params.smoothing_window > 0
    assert params.smoothing_window % 2 == 1  # Must be odd
    assert params.polyorder >= 2


def test_auto_tune_parameters_accurate_preset() -> None:
    """Test auto_tune_parameters with accurate quality preset."""
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.7,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="medium",
    )

    params = auto_tune_parameters(chars, QualityPreset.ACCURATE)

    # Accurate preset should produce valid parameters
    assert isinstance(params, AnalysisParameters)
    assert params.smoothing_window > 0
    assert params.smoothing_window % 2 == 1  # Must be odd
    assert params.polyorder >= 2


def test_auto_tune_parameters_fps_scaling() -> None:
    """Test auto_tune_parameters handles different FPS values."""
    chars_30fps = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.7,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="medium",
    )

    chars_60fps = VideoCharacteristics(
        fps=60.0,
        frame_count=600,
        avg_visibility=0.7,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="medium",
    )

    params_30 = auto_tune_parameters(chars_30fps, QualityPreset.BALANCED)
    params_60 = auto_tune_parameters(chars_60fps, QualityPreset.BALANCED)

    # Both should produce valid parameters
    assert isinstance(params_30, AnalysisParameters)
    assert isinstance(params_60, AnalysisParameters)
    assert params_30.smoothing_window > 0
    assert params_60.smoothing_window > 0


def test_auto_tune_parameters_default_preset() -> None:
    """Test auto_tune_parameters uses balanced preset by default."""
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.7,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="medium",
    )

    params_default = auto_tune_parameters(chars)
    params_balanced = auto_tune_parameters(chars, QualityPreset.BALANCED)

    # Should produce same results
    assert params_default.smoothing_window == params_balanced.smoothing_window
    assert params_default.polyorder == params_balanced.polyorder


def test_auto_tune_parameters_visibility_threshold_adaptation() -> None:
    """Test visibility threshold adapts to video quality."""
    chars_high = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.9,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="high",
    )

    chars_low = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.3,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="low",
    )

    params_high = auto_tune_parameters(chars_high, QualityPreset.BALANCED)
    params_low = auto_tune_parameters(chars_low, QualityPreset.BALANCED)

    # Low quality video should have lower visibility threshold
    assert params_low.visibility_threshold <= params_high.visibility_threshold


def test_auto_tune_parameters_always_enables_curvature() -> None:
    """Test auto_tune_parameters always enables curvature analysis."""
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=300,
        avg_visibility=0.7,
        position_variance=0.01,
        has_stable_period=True,
        tracking_quality="medium",
    )

    params_fast = auto_tune_parameters(chars, QualityPreset.FAST)
    params_balanced = auto_tune_parameters(chars, QualityPreset.BALANCED)
    params_accurate = auto_tune_parameters(chars, QualityPreset.ACCURATE)

    # Curvature should be enabled for all presets (proven feature)
    assert params_fast.use_curvature is True
    assert params_balanced.use_curvature is True
    assert params_accurate.use_curvature is True


# ===== Integration Tests =====


def test_full_auto_tuning_workflow() -> None:
    """Test complete auto-tuning workflow from characteristics to parameters."""
    # Analyze video characteristics
    chars = VideoCharacteristics(
        fps=30.0,
        frame_count=450,
        avg_visibility=0.75,
        position_variance=0.012,
        has_stable_period=True,
        tracking_quality="medium",
    )

    # Verify tracking quality classification
    quality = analyze_tracking_quality(chars.avg_visibility)
    assert quality == "high"  # 0.75 > 0.7

    # Auto-tune parameters
    params = auto_tune_parameters(chars, QualityPreset.BALANCED)

    # Verify parameters are reasonable
    assert params.smoothing_window >= 5
    assert params.polyorder >= 2
    # Updated to reflect empirically-validated velocity threshold
    # (0.002 at 60fps, 0.004 at 30fps)
    assert 0.001 <= params.velocity_threshold <= 0.05
    assert params.min_contact_frames >= 3
    assert 0.3 <= params.visibility_threshold <= 0.7
    assert 0.3 <= params.detection_confidence <= 0.7
    assert 0.3 <= params.tracking_confidence <= 0.7

    # Convert to dict
    params_dict = params.to_dict()
    assert isinstance(params_dict, dict)
    assert len(params_dict) == 10
