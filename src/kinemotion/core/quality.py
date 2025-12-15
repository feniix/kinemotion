"""Quality assessment and confidence scoring for pose tracking and analysis."""

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray


@dataclass
class QualityIndicators:
    """Detailed quality indicators for pose tracking and analysis.

    Attributes:
        avg_visibility: Mean visibility score across all key landmarks (0-1)
        min_visibility: Minimum visibility score encountered (0-1)
        tracking_stable: Whether landmark tracking was stable (low jitter)
        phase_detection_clear: Whether phase transitions were clearly detected
        outliers_detected: Number of outlier frames detected and corrected
        outlier_percentage: Percentage of frames with outliers (0-100)
        position_variance: Variance in position tracking (lower is more stable)
        fps: Video frame rate (higher is better for accuracy)
    """

    avg_visibility: float
    min_visibility: float
    tracking_stable: bool
    phase_detection_clear: bool
    outliers_detected: int
    outlier_percentage: float
    position_variance: float
    fps: float


@dataclass
class QualityAssessment:
    """Overall quality assessment with confidence level and warnings.

    Attributes:
        confidence: Overall confidence level (high/medium/low)
        quality_indicators: Detailed quality metrics
        warnings: List of warning messages for user
        quality_score: Numerical quality score (0-100)
    """

    confidence: Literal["high", "medium", "low"]
    quality_indicators: QualityIndicators
    warnings: list[str]
    quality_score: float

    def to_dict(self) -> dict:
        """Convert quality assessment to JSON-serializable dictionary."""
        return {
            "confidence": self.confidence,
            "quality_score": round(self.quality_score, 1),
            "quality_indicators": {
                "avg_visibility": round(self.quality_indicators.avg_visibility, 3),
                "min_visibility": round(self.quality_indicators.min_visibility, 3),
                "tracking_stable": self.quality_indicators.tracking_stable,
                "phase_detection_clear": self.quality_indicators.phase_detection_clear,
                "outliers_detected": self.quality_indicators.outliers_detected,
                "outlier_percentage": round(self.quality_indicators.outlier_percentage, 1),
                "position_variance": round(self.quality_indicators.position_variance, 6),
                "fps": round(self.quality_indicators.fps, 1),
            },
            "warnings": self.warnings,
        }


def calculate_position_stability(
    positions: NDArray[np.float64],
    window_size: int = 10,
) -> float:
    """
    Calculate position tracking stability using rolling variance.

    Lower variance indicates more stable tracking (less jitter).

    Args:
        positions: Array of position values (e.g., foot y-positions)
        window_size: Window size for rolling variance calculation

    Returns:
        Mean rolling variance (lower is better)
    """
    if len(positions) < window_size:
        return float(np.var(positions))

    # Calculate rolling variance
    rolling_vars = []
    for i in range(len(positions) - window_size + 1):
        window = positions[i : i + window_size]
        rolling_vars.append(np.var(window))

    return float(np.mean(rolling_vars))


def assess_tracking_quality(
    visibilities: NDArray[np.float64],
    positions: NDArray[np.float64],
    outlier_mask: NDArray[np.bool_] | None,
    fps: float,
    phases_detected: bool = True,
    phase_count: int = 0,
) -> QualityAssessment:
    """
    Assess overall tracking quality and assign confidence level.

    Evaluates multiple quality indicators to determine confidence:
    - Landmark visibility (MediaPipe confidence scores)
    - Tracking stability (position variance, jitter)
    - Outlier detection (frames requiring correction)
    - Phase detection success (clear transitions found)
    - Frame rate (higher = better temporal resolution)

    Args:
        visibilities: Array of visibility scores for each frame (0-1)
        positions: Array of tracked positions (normalized coordinates)
        outlier_mask: Boolean array marking outlier frames (None if no outliers)
        fps: Video frame rate
        phases_detected: Whether jump phases were successfully detected
        phase_count: Number of phases detected (0 if failed)

    Returns:
        QualityAssessment object with confidence level, indicators, and warnings
    """
    # Calculate visibility metrics
    avg_visibility = float(np.mean(visibilities))
    min_visibility = float(np.min(visibilities))

    # Calculate tracking stability
    position_variance = calculate_position_stability(positions)
    tracking_stable = position_variance < 0.001  # Threshold for stable tracking

    # Count outliers
    outliers_detected = 0
    outlier_percentage = 0.0
    if outlier_mask is not None:
        outliers_detected = int(np.sum(outlier_mask))
        outlier_percentage = (outliers_detected / len(outlier_mask)) * 100

    # Assess phase detection clarity
    phase_detection_clear = phases_detected and phase_count >= 2

    # Create quality indicators
    indicators = QualityIndicators(
        avg_visibility=avg_visibility,
        min_visibility=min_visibility,
        tracking_stable=tracking_stable,
        phase_detection_clear=phase_detection_clear,
        outliers_detected=outliers_detected,
        outlier_percentage=outlier_percentage,
        position_variance=position_variance,
        fps=fps,
    )

    # Calculate overall quality score (0-100)
    quality_score = _calculate_quality_score(indicators)

    # Determine confidence level
    confidence = _determine_confidence_level(quality_score)

    # Generate warnings
    warnings = _generate_warnings(indicators, confidence)

    return QualityAssessment(
        confidence=confidence,
        quality_indicators=indicators,
        warnings=warnings,
        quality_score=quality_score,
    )


def _calculate_quality_score(indicators: QualityIndicators) -> float:
    """
    Calculate numerical quality score (0-100) from quality indicators.

    Weighted combination of different quality factors:
    - Visibility: 40% weight (most critical)
    - Tracking stability: 25% weight
    - Outlier rate: 20% weight
    - Phase detection: 10% weight
    - Frame rate: 5% weight

    Args:
        indicators: Quality indicators object

    Returns:
        Quality score from 0 (worst) to 100 (best)
    """
    # Visibility score (40% weight)
    # Perfect: avg_vis=1.0, min_vis>0.8
    visibility_score = indicators.avg_visibility * 100
    if indicators.min_visibility < 0.5:
        visibility_score *= 0.7  # Penalty for low minimum visibility

    # Tracking stability score (25% weight)
    # Perfect: position_variance < 0.0005
    # Good: position_variance < 0.001
    # Medium: position_variance < 0.003
    if indicators.position_variance < 0.0005:
        stability_score = 100.0
    elif indicators.position_variance < 0.001:
        stability_score = 85.0
    elif indicators.position_variance < 0.003:
        stability_score = 65.0
    else:
        stability_score = max(0.0, 100 - indicators.position_variance * 10000)

    # Outlier score (20% weight)
    # Perfect: 0% outliers
    # Good: <5% outliers
    # Acceptable: <10% outliers
    outlier_score = max(0.0, 100 - indicators.outlier_percentage * 10)

    # Phase detection score (10% weight)
    phase_score = 100.0 if indicators.phase_detection_clear else 50.0

    # Frame rate score (5% weight)
    # Perfect: 60fps+
    # Good: 30-60fps
    # Poor: <30fps
    if indicators.fps >= 60:
        fps_score = 100.0
    elif indicators.fps >= 30:
        fps_score = 80.0
    elif indicators.fps >= 24:
        fps_score = 60.0
    else:
        fps_score = 40.0

    # Weighted combination
    quality_score = (
        visibility_score * 0.40
        + stability_score * 0.25
        + outlier_score * 0.20
        + phase_score * 0.10
        + fps_score * 0.05
    )

    return float(np.clip(quality_score, 0, 100))


def _determine_confidence_level(
    quality_score: float,
) -> Literal["high", "medium", "low"]:
    """
    Determine confidence level from quality score.

    Thresholds:
    - High: quality_score >= 75
    - Medium: quality_score >= 50
    - Low: quality_score < 50

    Args:
        quality_score: Numerical quality score (0-100)

    Returns:
        Confidence level: "high", "medium", or "low"
    """
    if quality_score >= 75:
        return "high"
    elif quality_score >= 50:
        return "medium"
    else:
        return "low"


def _generate_warnings(
    indicators: QualityIndicators,
    confidence: Literal["high", "medium", "low"],
) -> list[str]:
    """
    Generate user-facing warning messages based on quality indicators.

    Args:
        indicators: Quality indicators object
        confidence: Overall confidence level

    Returns:
        List of warning messages (empty if no warnings)
    """
    warnings: list[str] = []

    # Visibility warnings
    if indicators.avg_visibility < 0.7:
        warnings.append(
            f"Poor landmark visibility (avg {indicators.avg_visibility:.2f}). "
            "Check lighting, camera angle, and ensure full body is visible."
        )
    elif indicators.avg_visibility < 0.8:
        warnings.append(
            f"Moderate landmark visibility (avg {indicators.avg_visibility:.2f}). "
            "Results may be less accurate."
        )

    if indicators.min_visibility < 0.5:
        warnings.append(
            f"Very low visibility detected ({indicators.min_visibility:.2f}). "
            "Some frames may have occlusion or tracking loss."
        )

    # Tracking stability warnings
    if not indicators.tracking_stable:
        warnings.append(
            f"Unstable landmark tracking detected "
            f"(variance {indicators.position_variance:.4f}). This may indicate "
            "jitter or occlusion. Consider better lighting or camera position."
        )

    # Outlier warnings
    if indicators.outlier_percentage > 10:
        warnings.append(
            f"High outlier rate ({indicators.outlier_percentage:.1f}%). "
            f"{indicators.outliers_detected} frames required correction. "
            "This may reduce measurement accuracy."
        )
    elif indicators.outlier_percentage > 5:
        warnings.append(
            f"Moderate outlier rate ({indicators.outlier_percentage:.1f}%). "
            f"{indicators.outliers_detected} frames were corrected."
        )

    # Phase detection warnings
    if not indicators.phase_detection_clear:
        warnings.append(
            "Unclear phase transitions detected. "
            "Jump phases may not be accurately identified. "
            "Check if full jump is captured in video."
        )

    # Frame rate warnings
    if indicators.fps < 30:
        warnings.append(
            f"Low frame rate ({indicators.fps:.0f} fps). "
            "Recommend recording at 30fps or higher for better accuracy. "
            "Validated apps use 120-240fps."
        )
    elif indicators.fps < 60:
        warnings.append(
            f"Frame rate is {indicators.fps:.0f} fps. "
            "Consider 60fps or higher for improved temporal resolution. "
            "Validated apps (MyJump) use 120-240fps."
        )

    # Overall confidence warning
    if confidence == "low":
        warnings.append(
            "⚠️ LOW CONFIDENCE: Results may be unreliable. Review quality "
            "indicators and consider re-recording with better conditions."
        )
    elif confidence == "medium":
        warnings.append(
            "⚠️ MEDIUM CONFIDENCE: Results should be interpreted with caution. "
            "Check quality indicators for specific issues."
        )

    return warnings


def assess_jump_quality(
    visibilities: NDArray[np.float64],
    positions: NDArray[np.float64],
    outlier_mask: NDArray[np.bool_] | None,
    fps: float,
    phases_detected: bool = True,
    phase_count: int = 0,
) -> QualityAssessment:
    """
    Convenience function for assessing jump analysis quality.

    This is the main entry point for quality assessment, called from
    dropjump and CMJ analysis modules.

    Args:
        visibilities: Array of visibility scores (0-1)
        positions: Array of tracked positions
        outlier_mask: Boolean array marking outliers (None if none detected)
        fps: Video frame rate
        phases_detected: Whether phases were successfully detected
        phase_count: Number of phases detected

    Returns:
        QualityAssessment with confidence, indicators, and warnings
    """
    return assess_tracking_quality(
        visibilities=visibilities,
        positions=positions,
        outlier_mask=outlier_mask,
        fps=fps,
        phases_detected=phases_detected,
        phase_count=phase_count,
    )
