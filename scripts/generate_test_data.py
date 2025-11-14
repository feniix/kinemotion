#!/usr/bin/env python3
"""Generate synthetic test data for known height validation testing.

This script creates JSON files that simulate kinemotion's output for
dropped objects at different heights, with realistic error patterns.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np


def create_synthetic_result(
    height_m: float,
    run_number: int,
    systematic_bias_ms: float = 0,
    random_error_ms: float = 5,
) -> dict:
    """Create a synthetic CMJ result JSON for a dropped object.

    Args:
        height_m: Drop height in meters
        run_number: Run number (1-30)
        systematic_bias_ms: Consistent error across all measurements
        random_error_ms: Random error added per run

    Returns:
        Dictionary matching kinemotion's JSON output format
    """
    # Calculate theoretical time
    g = 9.81
    theoretical_time = float(np.sqrt(2 * height_m / g))

    # Add systematic bias and random error
    random_component = np.random.normal(0, random_error_ms / 1000)
    measured_time = theoretical_time + (systematic_bias_ms / 1000) + random_component

    # Create realistic landing frame based on flight time
    fps = 60.0
    frames_in_air = int(measured_time * fps)
    landing_frame = 100 + frames_in_air

    return {
        "data": {
            "jump_height_m": measured_time**2 * 9.81 / 8,  # Derived from flight time
            "flight_time_s": float(measured_time),
            "countermovement_depth_m": 0.001,  # Minimal for dropped object
            "eccentric_duration_s": 0.01,
            "concentric_duration_s": 0.01,
            "total_movement_time_s": 0.02,
            "peak_eccentric_velocity_m_s": 0.01,
            "peak_concentric_velocity_m_s": -measured_time * 9.81 / 2,
            "transition_time_s": 0.005,
            "standing_start_frame": 50.0,
            "lowest_point_frame": 60.0,
            "takeoff_frame": 100.0,
            "landing_frame": float(landing_frame),
            "tracking_method": "foot",
        },
        "metadata": {
            "quality": {
                "confidence": "high",
                "quality_score": 90.0,
                "quality_indicators": {
                    "avg_visibility": 0.95,
                    "min_visibility": 0.92,
                    "tracking_stable": True,
                    "phase_detection_clear": True,
                    "outliers_detected": 0,
                    "outlier_percentage": 0.0,
                    "position_variance": 0.00001,
                    "fps": 60.0,
                },
                "warnings": [],
            },
            "video": {
                "source_path": f"data/known_heights/videos/drop_{height_m}m_run{run_number}.mp4",
                "fps": 60.0,
                "resolution": {"width": 1920, "height": 1080},
                "duration_s": 5.0,
                "frame_count": 300,
                "codec": None,
            },
            "processing": {
                "version": "0.24.0",
                "timestamp": datetime.utcnow().isoformat() + "+00:00",
                "quality_preset": "balanced",
                "processing_time_s": 2.5,
            },
            "algorithm": {
                "detection_method": "backward_search",
                "tracking_method": "mediapipe_pose",
                "model_complexity": 1,
                "smoothing": {
                    "window_size": 5,
                    "polynomial_order": 2,
                    "use_bilateral_filter": False,
                    "use_outlier_rejection": True,
                },
                "detection": {
                    "velocity_threshold": 0.0203,
                    "min_contact_frames": 3,
                    "visibility_threshold": 0.5,
                    "use_curvature_refinement": True,
                },
            },
        },
    }


def generate_test_dataset(
    output_dir: Path,
    heights: list[float] = None,
    runs_per_height: int = 10,
    systematic_bias_ms: float = 2,
    random_error_ms: float = 5,
) -> None:
    """Generate complete test dataset.

    Args:
        output_dir: Directory to save JSON files
        heights: Heights to test (default: [0.5, 1.0, 1.5])
        runs_per_height: Number of drops per height (default: 10)
        systematic_bias_ms: Consistent error across all (default: 2ms)
        random_error_ms: Random error per run (default: 5ms std)
    """
    if heights is None:
        heights = [0.5, 1.0, 1.5]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating test data: {runs_per_height} drops × {len(heights)} heights")
    print(f"Output directory: {output_dir}")
    print(f"Systematic bias: {systematic_bias_ms}ms")
    print(f"Random error: ±{random_error_ms}ms (1σ)")
    print()

    run_count = 0
    for height in heights:
        for run in range(1, runs_per_height + 1):
            run_count += 1

            # Generate result
            result = create_synthetic_result(
                height_m=height,
                run_number=run,
                systematic_bias_ms=systematic_bias_ms,
                random_error_ms=random_error_ms,
            )

            # Save JSON
            filename = f"drop_{height}m_run{run}.json"
            filepath = output_dir / filename

            with open(filepath, "w") as f:
                json.dump(result, f, indent=2)

            # Print progress
            if run % 5 == 0 or run == runs_per_height:
                measured = result["data"]["flight_time_s"]
                theoretical = float(np.sqrt(2 * height / 9.81))
                error_ms = (measured - theoretical) * 1000
                print(
                    f"  [{run_count:2d}] {filename:25s} → "
                    f"Flight time: {measured:.4f}s (error: {error_ms:+.1f}ms)"
                )

    print()
    print(f"✅ Generated {run_count} synthetic results in {output_dir}")
    print()
    print("Next steps:")
    print(f"  python scripts/validate_known_heights.py --videos-dir {output_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic test data for validation testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default test data (30 videos)
  python scripts/generate_test_data.py

  # Generate with custom output directory
  python scripts/generate_test_data.py --output data/synthetic_drops

  # Generate with more runs (45 videos)
  python scripts/generate_test_data.py --runs-per-height 15

  # Generate with higher systematic bias
  python scripts/generate_test_data.py --bias 10
        """,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/synthetic_drops"),
        help="Output directory (default: data/synthetic_drops)",
    )

    parser.add_argument(
        "--heights",
        nargs="+",
        type=float,
        default=[0.5, 1.0, 1.5],
        help="Heights to test in meters (default: 0.5 1.0 1.5)",
    )

    parser.add_argument(
        "--runs-per-height",
        type=int,
        default=10,
        help="Number of drops per height (default: 10)",
    )

    parser.add_argument(
        "--bias",
        type=float,
        default=2,
        help="Systematic bias in ms (default: 2)",
    )

    parser.add_argument(
        "--noise",
        type=float,
        default=5,
        help="Random error std dev in ms (default: 5)",
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )

    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    try:
        generate_test_dataset(
            output_dir=args.output,
            heights=args.heights,
            runs_per_height=args.runs_per_height,
            systematic_bias_ms=args.bias,
            random_error_ms=args.noise,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
