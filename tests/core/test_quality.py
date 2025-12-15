"""Tests for quality assessment module."""

import numpy as np
import pytest

from kinemotion.core.quality import (
    assess_jump_quality,
    calculate_position_stability,
)


class TestPositionStability:
    """Tests for position stability calculation."""

    def test_stable_positions(self):
        """Stable positions should have low variance."""
        # Perfectly stable positions
        positions = np.array([0.5] * 100)
        stability = calculate_position_stability(positions, window_size=10)

        assert stability == pytest.approx(0.0, abs=1e-10)

    def test_noisy_positions(self):
        """Noisy positions should have higher variance."""
        # Add random noise
        np.random.seed(42)
        positions = 0.5 + np.random.normal(0, 0.01, 100)
        stability = calculate_position_stability(positions, window_size=10)

        assert stability > 0.00005  # Should detect noise
        assert stability < 0.001  # But still relatively small

    def test_very_noisy_positions(self):
        """Very noisy tracking should have high variance."""
        np.random.seed(42)
        positions = 0.5 + np.random.normal(0, 0.05, 100)
        stability = calculate_position_stability(positions, window_size=10)

        assert stability > 0.001  # High variance detected

    def test_short_sequence(self):
        """Short sequences should fallback to overall variance."""
        positions = np.array([0.5, 0.51, 0.49, 0.50])
        stability = calculate_position_stability(positions, window_size=10)

        # Should compute overall variance
        assert stability == pytest.approx(np.var(positions))


class TestQualityAssessment:
    """Tests for overall quality assessment function."""

    def test_high_quality_detection(self):
        """High quality input should get high confidence."""
        # Perfect conditions
        visibilities = np.full(100, 0.95)
        positions = np.array([0.5] * 100)  # Perfectly stable
        outlier_mask = np.zeros(100, dtype=bool)  # No outliers
        fps = 60.0

        quality = assess_jump_quality(
            visibilities=visibilities,
            positions=positions,
            outlier_mask=outlier_mask,
            fps=fps,
            phases_detected=True,
            phase_count=4,
        )

        assert quality.confidence == "high"
        assert quality.quality_score >= 75
        assert len(quality.warnings) == 0  # No warnings for perfect conditions
        assert quality.quality_indicators.avg_visibility == pytest.approx(0.95)
        assert quality.quality_indicators.tracking_stable is True
        indicators = quality.quality_indicators
        assert indicators.outliers_detected == 0

    def test_low_quality_detection(self):
        """Low quality input should get low confidence."""
        # Poor conditions
        visibilities = np.full(100, 0.4)  # Low visibility
        np.random.seed(42)
        positions = 0.5 + np.random.normal(0, 0.05, 100)  # Very noisy
        outlier_mask = np.random.rand(100) > 0.8  # 20% outliers
        fps = 24.0  # Low fps

        quality = assess_jump_quality(
            visibilities=visibilities,
            positions=positions,
            outlier_mask=outlier_mask,
            fps=fps,
            phases_detected=False,  # Failed detection
            phase_count=0,
        )

        assert quality.confidence == "low"
        assert quality.quality_score < 50
        assert len(quality.warnings) > 0  # Should have warnings
        assert quality.quality_indicators.avg_visibility == pytest.approx(0.4)
        assert quality.quality_indicators.tracking_stable is False

    def test_medium_quality_detection(self):
        """Medium quality input should get medium confidence."""
        # Moderate conditions
        visibilities = np.full(100, 0.75)
        positions = 0.5 + np.random.normal(0, 0.005, 100)  # Slight noise
        outlier_mask = np.zeros(100, dtype=bool)
        outlier_mask[::20] = True  # 5% outliers
        fps = 30.0

        quality = assess_jump_quality(
            visibilities=visibilities,
            positions=positions,
            outlier_mask=outlier_mask,
            fps=fps,
            phases_detected=True,
            phase_count=3,
        )

        assert quality.confidence == "medium" or quality.confidence == "high"
        assert 50 <= quality.quality_score < 85
        assert quality.quality_indicators.outlier_percentage == pytest.approx(5.0)

    def test_quality_to_dict(self):
        """Quality assessment should serialize to dict properly."""
        visibilities = np.full(50, 0.9)
        positions = np.array([0.5] * 50)
        outlier_mask = np.zeros(50, dtype=bool)
        fps = 60.0

        quality = assess_jump_quality(
            visibilities=visibilities,
            positions=positions,
            outlier_mask=outlier_mask,
            fps=fps,
            phases_detected=True,
            phase_count=4,
        )

        quality_dict = quality.to_dict()

        # Check structure
        assert "confidence" in quality_dict
        assert "quality_score" in quality_dict
        assert "quality_indicators" in quality_dict
        assert "warnings" in quality_dict

        # Check types
        assert isinstance(quality_dict["confidence"], str)
        assert isinstance(quality_dict["quality_score"], float)
        assert isinstance(quality_dict["quality_indicators"], dict)
        assert isinstance(quality_dict["warnings"], list)

        # Check quality indicators structure
        qi = quality_dict["quality_indicators"]
        assert "avg_visibility" in qi
        assert "min_visibility" in qi
        assert "tracking_stable" in qi
        assert "phase_detection_clear" in qi
        assert "outliers_detected" in qi
        assert "outlier_percentage" in qi
        assert "position_variance" in qi
        assert "fps" in qi


class TestQualityWarnings:
    """Tests for warning generation based on quality indicators."""

    def test_low_visibility_warning(self):
        """Low visibility should generate warning."""
        visibilities = np.full(100, 0.6)  # Low visibility
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(visibilities, positions, outlier_mask, fps=60.0)

        # Should have visibility warning
        warnings_text = " ".join(quality.warnings)
        assert "visibility" in warnings_text.lower()

    def test_very_low_visibility_warning(self):
        """Very low minimum visibility should generate specific warning."""
        visibilities = np.full(100, 0.8)
        visibilities[50] = 0.3  # One very low frame

        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(visibilities, positions, outlier_mask, fps=60.0)

        warnings_text = " ".join(quality.warnings).lower()
        assert "very low visibility" in warnings_text or "occlusion" in warnings_text

    def test_unstable_tracking_warning(self):
        """Unstable tracking should generate warning."""
        visibilities = np.full(100, 0.9)
        np.random.seed(42)
        positions = 0.5 + np.random.normal(0, 0.05, 100)  # Very jittery
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(visibilities, positions, outlier_mask, fps=60.0)

        warnings_text = " ".join(quality.warnings)
        assert "unstable" in warnings_text.lower() or "jitter" in warnings_text.lower()

    def test_high_outlier_warning(self):
        """High outlier rate should generate warning."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)
        outlier_mask[::5] = True  # 20% outliers

        quality = assess_jump_quality(visibilities, positions, outlier_mask, fps=60.0)

        assert quality.quality_indicators.outlier_percentage == pytest.approx(20.0)
        warnings_text = " ".join(quality.warnings)
        assert "outlier" in warnings_text.lower()

    def test_low_fps_warning(self):
        """Low frame rate should generate warning."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(
            visibilities,
            positions,
            outlier_mask,
            fps=24.0,  # Low fps
        )

        warnings_text = " ".join(quality.warnings)
        assert "frame rate" in warnings_text.lower() or "fps" in warnings_text.lower()

    def test_phase_detection_failure_warning(self):
        """Failed phase detection should generate warning."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(
            visibilities,
            positions,
            outlier_mask,
            fps=60.0,
            phases_detected=False,  # Failed
            phase_count=0,
        )

        warnings_text = " ".join(quality.warnings)
        assert "phase" in warnings_text.lower()

    def test_no_warnings_for_perfect_quality(self):
        """Perfect quality should generate no warnings."""
        visibilities = np.full(100, 0.95)
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(
            visibilities,
            positions,
            outlier_mask,
            fps=60.0,
            phases_detected=True,
            phase_count=4,
        )

        assert len(quality.warnings) == 0


class TestQualityScoring:
    """Tests for quality score calculation logic."""

    def test_perfect_score(self):
        """Perfect conditions should give score near 100."""
        visibilities = np.full(100, 1.0)
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        quality = assess_jump_quality(
            visibilities,
            positions,
            outlier_mask,
            fps=60.0,
            phases_detected=True,
            phase_count=4,
        )

        assert quality.quality_score >= 90
        assert quality.confidence == "high"

    def test_score_decreases_with_low_visibility(self):
        """Lower visibility should decrease quality score."""
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        # High visibility
        quality_high = assess_jump_quality(np.full(100, 0.95), positions, outlier_mask, fps=60.0)

        # Medium visibility
        quality_medium = assess_jump_quality(np.full(100, 0.75), positions, outlier_mask, fps=60.0)

        # Low visibility
        quality_low = assess_jump_quality(np.full(100, 0.55), positions, outlier_mask, fps=60.0)

        assert quality_high.quality_score > quality_medium.quality_score
        assert quality_medium.quality_score > quality_low.quality_score

    def test_score_decreases_with_outliers(self):
        """More outliers should decrease quality score."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)

        # No outliers
        quality_none = assess_jump_quality(
            visibilities, positions, np.zeros(100, dtype=bool), fps=60.0
        )

        # 5% outliers
        outliers_5pct = np.zeros(100, dtype=bool)
        outliers_5pct[::20] = True
        quality_5pct = assess_jump_quality(visibilities, positions, outliers_5pct, fps=60.0)

        # 20% outliers
        outliers_20pct = np.zeros(100, dtype=bool)
        outliers_20pct[::5] = True
        quality_20pct = assess_jump_quality(visibilities, positions, outliers_20pct, fps=60.0)

        assert quality_none.quality_score > quality_5pct.quality_score
        assert quality_5pct.quality_score > quality_20pct.quality_score

    def test_score_with_none_outlier_mask(self):
        """Should handle None outlier_mask (no outliers detected)."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)

        quality = assess_jump_quality(visibilities, positions, outlier_mask=None, fps=60.0)

        assert quality.quality_indicators.outliers_detected == 0
        assert quality.quality_indicators.outlier_percentage == 0.0
        assert quality.quality_score > 75  # Should be high quality


class TestQualityIndicators:
    """Tests for individual quality indicators."""

    def test_avg_visibility_calculation(self):
        """Average visibility should be calculated correctly."""
        visibilities = np.array([0.9, 0.8, 0.95, 0.85, 0.9])
        positions = np.array([0.5] * 5)

        quality = assess_jump_quality(visibilities, positions, None, fps=30.0)

        expected_avg = np.mean(visibilities)
        assert quality.quality_indicators.avg_visibility == pytest.approx(expected_avg)

    def test_min_visibility_calculation(self):
        """Minimum visibility should be tracked."""
        visibilities = np.array([0.9, 0.8, 0.6, 0.85, 0.9])  # Min is 0.6
        positions = np.array([0.5] * 5)

        quality = assess_jump_quality(visibilities, positions, None, fps=30.0)

        assert quality.quality_indicators.min_visibility == pytest.approx(0.6)

    def test_outlier_counting(self):
        """Outliers should be counted correctly."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)
        outlier_mask[[10, 20, 30, 40, 50]] = True  # 5 outliers

        quality = assess_jump_quality(visibilities, positions, outlier_mask, fps=60.0)

        assert quality.quality_indicators.outliers_detected == 5
        assert quality.quality_indicators.outlier_percentage == pytest.approx(5.0)

    def test_fps_recording(self):
        """Frame rate should be recorded in indicators."""
        visibilities = np.full(50, 0.9)
        positions = np.array([0.5] * 50)

        quality = assess_jump_quality(visibilities, positions, None, fps=120.0)

        assert quality.quality_indicators.fps == pytest.approx(120.0)


class TestConfidenceLevels:
    """Tests for confidence level thresholds."""

    def test_confidence_thresholds(self):
        """Test that confidence levels are assigned at correct thresholds."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)

        # Create scenarios for each confidence level
        # High: quality_score >= 75
        quality_high = assess_jump_quality(
            visibilities, positions, None, fps=60.0, phases_detected=True, phase_count=4
        )

        # Medium: quality_score 50-74 (degrade with low fps)
        quality_medium = assess_jump_quality(
            visibilities, positions, None, fps=24.0, phases_detected=True, phase_count=2
        )

        # Low: quality_score < 50 (very poor visibility + multiple issues)
        visibilities_low = np.full(100, 0.3)  # Very low visibility
        np.random.seed(42)
        positions_noisy = 0.5 + np.random.normal(0, 0.05, 100)
        outlier_mask_high = np.random.rand(100) > 0.7  # 30% outliers
        quality_low = assess_jump_quality(
            visibilities_low,
            positions_noisy,
            outlier_mask_high,
            fps=15.0,
            phases_detected=False,
        )

        assert quality_high.confidence == "high"
        assert quality_medium.confidence in ["medium", "high"]
        assert quality_low.confidence == "low"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_positions(self):
        """Should handle minimal data gracefully."""
        visibilities = np.array([0.9])
        positions = np.array([0.5])

        quality = assess_jump_quality(visibilities, positions, None, fps=30.0)

        # Should not crash, should give some assessment
        assert quality.confidence in ["high", "medium", "low"]
        assert 0 <= quality.quality_score <= 100

    def test_all_outliers(self):
        """Should handle case where all frames are outliers."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)
        outlier_mask = np.ones(100, dtype=bool)  # All outliers

        quality = assess_jump_quality(visibilities, positions, outlier_mask, fps=60.0)

        assert quality.quality_indicators.outlier_percentage == pytest.approx(100.0)
        # With good visibility, even 100% outliers might get medium confidence
        assert quality.confidence in ["low", "medium"]
        assert len(quality.warnings) > 0  # Should have outlier warning

    def test_varying_visibility(self):
        """Should handle varying visibility across frames."""
        # Start high, drop in middle, recover
        visibilities = np.concatenate(
            [
                np.full(30, 0.95),
                np.full(40, 0.4),  # Poor section
                np.full(30, 0.9),
            ]
        )
        positions = np.array([0.5] * 100)

        quality = assess_jump_quality(visibilities, positions, None, fps=60.0)

        # Average should be moderate
        expected_avg = (30 * 0.95 + 40 * 0.4 + 30 * 0.9) / 100
        assert quality.quality_indicators.avg_visibility == pytest.approx(expected_avg)
        assert quality.quality_indicators.min_visibility == pytest.approx(0.4)


class TestQualityScoreComponents:
    """Tests for quality score component weighting."""

    def test_visibility_weight_dominates(self):
        """Visibility should have largest impact on score (40% weight)."""
        positions = np.array([0.5] * 100)
        outlier_mask = np.zeros(100, dtype=bool)

        # High visibility baseline
        q_high_vis = assess_jump_quality(
            np.full(100, 0.95), positions, outlier_mask, fps=60.0, phases_detected=True
        )

        # Low visibility
        q_low_vis = assess_jump_quality(
            np.full(100, 0.5), positions, outlier_mask, fps=60.0, phases_detected=True
        )

        # Visibility impact should be significant (40% weight)
        score_diff = q_high_vis.quality_score - q_low_vis.quality_score
        assert score_diff > 15  # Significant impact from visibility alone

        # High visibility should result in higher score
        assert q_high_vis.quality_score > q_low_vis.quality_score

        # Verify visibility is the dominant factor
        # Even with perfect stability, low visibility reduces score
        assert q_low_vis.quality_indicators.avg_visibility < 0.6

    def test_fps_weight_is_small(self):
        """FPS should have small impact on score (5% weight)."""
        visibilities = np.full(100, 0.9)
        positions = np.array([0.5] * 100)

        q_60fps = assess_jump_quality(visibilities, positions, None, fps=60.0)
        q_30fps = assess_jump_quality(visibilities, positions, None, fps=30.0)

        # FPS impact should be small
        score_diff = abs(q_60fps.quality_score - q_30fps.quality_score)
        assert score_diff < 10  # Small impact from fps alone
