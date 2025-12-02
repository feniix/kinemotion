#!/usr/bin/env python3
"""Validate kinemotion timing accuracy using physics of falling objects.

This script validates the accuracy of flight time measurements by comparing
measured values against theoretical predictions from physics equations.

Test Protocol:
- Drop object from measured heights (0.5m, 1.0m, 1.5m)
- Record video at 60fps
- Compare kinemotion's flight_time measurement against theoretical value
- Use formula: t = sqrt(2*h/g) where g = 9.81 m/s²

Expected Results:
- Mean absolute error (MAE) < 20ms
- RMSE < 30ms
- Correlation > 0.99 with theoretical values
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class PhysicsValidationResult:
    """Result of physics validation for a single video."""

    video_path: str
    true_height_m: float
    measured_flight_time_s: float
    theoretical_flight_time_s: float
    absolute_error_ms: float
    percent_error: float
    confidence: str


def calculate_theoretical_time(height_m: float) -> float:
    """Calculate theoretical flight time using physics.

    For a freely falling object: t = sqrt(2*h/g)
    where h = height (m), g = 9.81 m/s²

    Args:
        height_m: Drop height in meters

    Returns:
        Expected flight time in seconds
    """
    g = 9.81  # gravitational acceleration
    return float(np.sqrt(2 * height_m / g))


def extract_filename_height(filename: str) -> float | None:
    """Extract height from filename.

    Expected format: "drop_[HEIGHT]m.mp4" or "drop_[HEIGHT]_[RUN].mp4"
    Examples: "drop_0.5m.mp4", "drop_1.0m_run1.mp4"

    Args:
        filename: Video filename

    Returns:
        Height in meters, or None if format not recognized
    """
    import re

    # Pattern: matches "drop_" followed by a number with optional decimal
    match = re.search(r"drop_(\d+\.?\d*)m", filename)
    if match:
        return float(match.group(1))
    return None


def validate_video(video_path: str, true_height_m: float) -> PhysicsValidationResult:
    """Validate a single drop video against physics predictions.

    Args:
        video_path: Path to video file
        true_height_m: Actual drop height in meters

    Returns:
        PhysicsValidationResult with measurements and errors
    """
    from kinemotion import process_dropjump_video

    try:
        # Process video with kinemotion
        metrics_dict = process_dropjump_video(video_path, quality="balanced")

        # Extract flight time from new data/metadata structure
        if isinstance(metrics_dict, dict) and "data" in metrics_dict:
            flight_time = metrics_dict["data"].get("flight_time_s")
        else:
            flight_time = metrics_dict.get("flight_time_s")

        if flight_time is None:
            raise ValueError(f"No flight_time found in result for {video_path}")

        # Calculate theoretical time
        theoretical_time = calculate_theoretical_time(true_height_m)

        # Calculate errors
        absolute_error = flight_time - theoretical_time
        absolute_error_ms = absolute_error * 1000
        percent_error = (absolute_error / theoretical_time) * 100

        # Assess confidence (based on error magnitude)
        if abs(absolute_error_ms) < 10:
            confidence = "high"
        elif abs(absolute_error_ms) < 20:
            confidence = "medium"
        else:
            confidence = "low"

        return PhysicsValidationResult(
            video_path=str(video_path),
            true_height_m=true_height_m,
            measured_flight_time_s=flight_time,
            theoretical_flight_time_s=theoretical_time,
            absolute_error_ms=absolute_error_ms,
            percent_error=percent_error,
            confidence=confidence,
        )

    except Exception as e:
        print(f"Error processing {video_path}: {e}", file=sys.stderr)
        raise


def analyze_results(results: list[PhysicsValidationResult]) -> dict:
    """Analyze validation results and calculate summary statistics.

    Args:
        results: List of validation results

    Returns:
        Dict with summary statistics
    """
    if not results:
        return {}

    errors_ms = np.array([r.absolute_error_ms for r in results])
    percent_errors = np.array([r.percent_error for r in results])

    measured_times = np.array([r.measured_flight_time_s for r in results])
    theoretical_times = np.array([r.theoretical_flight_time_s for r in results])

    # Calculate correlation
    correlation = float(np.corrcoef(measured_times, theoretical_times)[0, 1])

    # Calculate statistics
    mae = float(np.mean(np.abs(errors_ms)))
    rmse = float(np.sqrt(np.mean(errors_ms**2)))
    bias = float(np.mean(errors_ms))
    std = float(np.std(errors_ms))

    # Count by confidence level
    high_confidence = sum(1 for r in results if r.confidence == "high")
    medium_confidence = sum(1 for r in results if r.confidence == "medium")
    low_confidence = sum(1 for r in results if r.confidence == "low")

    return {
        "total_videos": len(results),
        "mae_ms": mae,
        "rmse_ms": rmse,
        "bias_ms": bias,
        "std_ms": std,
        "correlation": correlation,
        "min_error_ms": float(np.min(np.abs(errors_ms))),
        "max_error_ms": float(np.max(np.abs(errors_ms))),
        "percent_error_mean": float(np.mean(np.abs(percent_errors))),
        "percent_error_std": float(np.std(percent_errors)),
        "confidence_distribution": {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence,
        },
        "pass_mae": mae < 20,
        "pass_rmse": rmse < 30,
        "pass_correlation": correlation > 0.99,
    }


def validate_directory(
    videos_dir: Path, output_json: Path | None = None
) -> tuple[list[PhysicsValidationResult], dict]:
    """Validate all videos or test results in a directory.

    Directory should contain videos with height encoded in filename:
    - drop_0.5m_run1.mp4  (actual videos)
    - drop_0.5m_run1.json (test data)

    Args:
        videos_dir: Directory containing video files or test JSON results
        output_json: Optional path to save results as JSON

    Returns:
        Tuple of (results list, summary statistics dict)
    """
    videos_dir = Path(videos_dir)

    if not videos_dir.exists():
        raise FileNotFoundError(f"Videos directory not found: {videos_dir}")

    # Find all mp4 files first, then fall back to JSON test files
    video_files = sorted(videos_dir.glob("drop_*.mp4"))
    is_test_data = False

    if not video_files:
        # Try to find JSON test data files
        video_files = sorted(videos_dir.glob("drop_*.json"))
        is_test_data = True

    if not video_files:
        print(
            f"Warning: No files found matching 'drop_*.mp4' or 'drop_*.json' in {videos_dir}"
        )
        print("Expected format: drop_0.5m_run1.mp4 or drop_0.5m_run1.json")
        return [], {}

    if is_test_data:
        print(f"Found {len(video_files)} test data files (JSON)")
    else:
        print(f"Found {len(video_files)} videos to validate")
    print("=" * 70)

    results = []

    for i, video_path in enumerate(video_files, 1):
        # Extract height from filename
        height = extract_filename_height(video_path.name)

        if height is None:
            print(f"\n[{i}/{len(video_files)}] ⚠️  {video_path.name}")
            print("  Could not extract height from filename")
            print("  Expected format: drop_0.5m_run1.mp4 or drop_0.5m_run1.json")
            continue

        print(f"\n[{i}/{len(video_files)}] {video_path.name}")
        print(f"  True height: {height:.2f}m")

        try:
            if is_test_data:
                # Load test data from JSON
                with open(video_path) as f:
                    test_result = json.load(f)

                measured_time = test_result["data"]["flight_time_s"]
                theoretical_time = calculate_theoretical_time(height)
                absolute_error = measured_time - theoretical_time
                absolute_error_ms = absolute_error * 1000
                percent_error = (absolute_error / theoretical_time) * 100

                if abs(absolute_error_ms) < 10:
                    confidence = "high"
                elif abs(absolute_error_ms) < 20:
                    confidence = "medium"
                else:
                    confidence = "low"

                result = PhysicsValidationResult(
                    video_path=str(video_path),
                    true_height_m=height,
                    measured_flight_time_s=measured_time,
                    theoretical_flight_time_s=theoretical_time,
                    absolute_error_ms=absolute_error_ms,
                    percent_error=percent_error,
                    confidence=confidence,
                )
            else:
                # Process actual video
                result = validate_video(str(video_path), height)

            results.append(result)

            theoretical = result.theoretical_flight_time_s
            measured = result.measured_flight_time_s
            error = result.absolute_error_ms

            status = (
                "✅"
                if result.confidence == "high"
                else "⚠️ "
                if result.confidence == "medium"
                else "❌"
            )

            print(
                f"  {status} Measured: {measured:.4f}s | Theoretical: {theoretical:.4f}s"
            )
            print(f"    Error: {error:+.2f}ms ({result.percent_error:+.1f}%)")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Analyze results
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    summary = analyze_results(results)

    if results:
        print(f"\nTotal videos processed: {summary['total_videos']}")
        print("\nTiming Accuracy:")
        mae_status = "✅" if summary["pass_mae"] else "❌"
        print(f"  Mean Absolute Error (MAE):  {summary['mae_ms']:.2f}ms {mae_status}")
        rmse_status = "✅" if summary["pass_rmse"] else "❌"
        print(
            f"  Root Mean Square Error (RMSE): {summary['rmse_ms']:.2f}ms {rmse_status}"
        )
        print(f"  Systematic Bias:            {summary['bias_ms']:+.2f}ms")
        print(f"  Standard Deviation:         {summary['std_ms']:.2f}ms")
        min_err = summary["min_error_ms"]
        max_err = summary["max_error_ms"]
        print(f"  Min/Max Error:              {min_err:.2f}ms / {max_err:.2f}ms")

        print("\nCorrelation with Physics:")
        corr_status = "✅" if summary["pass_correlation"] else "❌"
        print(
            f"  Pearson r:                  {summary['correlation']:.6f} {corr_status}"
        )

        print("\nPercent Error Statistics:")
        print(f"  Mean Absolute %:            {summary['percent_error_mean']:.2f}%")
        print(f"  Std Dev %:                  {summary['percent_error_std']:.2f}%")

        print("\nConfidence Distribution:")
        print(
            f"  High confidence:            {summary['confidence_distribution']['high']} videos"
        )
        print(
            f"  Medium confidence:          {summary['confidence_distribution']['medium']} videos"
        )
        print(
            f"  Low confidence:             {summary['confidence_distribution']['low']} videos"
        )

        # Overall pass/fail
        print("\n" + "-" * 70)
        all_pass = (
            summary["pass_mae"] and summary["pass_rmse"] and summary["pass_correlation"]
        )
        if all_pass:
            print("✅ VALIDATION PASSED - Algorithm meets accuracy requirements")
        else:
            print("❌ VALIDATION FAILED - Some criteria not met:")
            if not summary["pass_mae"]:
                print("   - MAE exceeds 20ms threshold")
            if not summary["pass_rmse"]:
                print("   - RMSE exceeds 30ms threshold")
            if not summary["pass_correlation"]:
                print("   - Correlation with physics < 0.99")

    else:
        print("No valid results to summarize")

    # Save results if requested
    if output_json and results:
        output_json = Path(output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "summary": summary,
            "results": [
                {
                    "video": r.video_path,
                    "true_height_m": r.true_height_m,
                    "measured_flight_time_s": r.measured_flight_time_s,
                    "theoretical_flight_time_s": r.theoretical_flight_time_s,
                    "absolute_error_ms": r.absolute_error_ms,
                    "percent_error": r.percent_error,
                    "confidence": r.confidence,
                }
                for r in results
            ],
        }

        with open(output_json, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to: {output_json}")

    return results, summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate kinemotion timing accuracy using physics of dropped objects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate videos in default location
  python scripts/validate_known_heights.py

  # Validate custom directory
  python scripts/validate_known_heights.py --videos-dir data/drops

  # Save results to JSON
  python scripts/validate_known_heights.py --output results.json

Video Filename Format:
  drop_0.5m_run1.mp4    (0.5m drop, run 1)
  drop_1.0m_run2.mp4    (1.0m drop, run 2)
  drop_1.5m_run3.mp4    (1.5m drop, run 3)
        """,
    )

    parser.add_argument(
        "--videos-dir",
        type=Path,
        default=Path("data/known_heights/videos"),
        help="Directory containing drop videos (default: data/known_heights/videos)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Save results to JSON file",
    )

    args = parser.parse_args()

    try:
        results, summary = validate_directory(args.videos_dir, args.output)
        exit_code = 0 if (summary.get("pass_mae") and summary.get("pass_rmse")) else 1
        sys.exit(exit_code)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
