#!/usr/bin/env python3
"""
Parameter optimization for CMJ and Drop Jump detection algorithms.

This script uses ground truth annotations to evaluate and optimize detection parameters.

Usage:
    # Evaluate current parameters
    python scripts/optimize_detection_params.py evaluate --ground-truth samples/validation/ground_truth.json

    # Run parameter optimization
    python scripts/optimize_detection_params.py optimize --ground-truth samples/validation/ground_truth.json --method grid

    # Test specific parameters
    python scripts/optimize_detection_params.py test --ground-truth samples/validation/ground_truth.json --params params.json
"""

import json
import sys
from pathlib import Path
from typing import Any

import click
import numpy as np
from scipy import optimize

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.api import process_cmj_video, process_dropjump_video


def load_ground_truth(filepath: Path) -> dict[str, Any]:
    """Load ground truth annotations from JSON file."""
    with open(filepath) as f:
        return json.load(f)


def compute_frame_error(predicted: float | None, ground_truth: float | None) -> float:
    """Compute absolute error between predicted and ground truth frame numbers."""
    if predicted is None or ground_truth is None:
        return float("nan")
    return abs(predicted - ground_truth)


def evaluate_cmj_detection(
    video_path: str,
    ground_truth: dict[str, float],
    fps: float,
    **params: Any,
) -> dict[str, float]:
    """
    Evaluate CMJ detection on a single video.

    Returns dict with errors for each event in frames.
    """
    try:
        # Run analysis with custom parameters
        result = process_cmj_video(video_path, **params)

        if result is None:
            return {
                "standing_end_error": float("nan"),
                "lowest_point_error": float("nan"),
                "takeoff_error": float("nan"),
                "landing_error": float("nan"),
            }

        # Convert to dict and extract data
        result_dict = result.to_dict()
        data = result_dict["data"]

        errors = {
            "standing_end_error": compute_frame_error(
                data.get("standing_start_frame"), ground_truth.get("standing_end")
            ),
            "lowest_point_error": compute_frame_error(
                data.get("lowest_point_frame"), ground_truth.get("lowest_point")
            ),
            "takeoff_error": compute_frame_error(
                data.get("takeoff_frame"), ground_truth.get("takeoff")
            ),
            "landing_error": compute_frame_error(
                data.get("landing_frame"), ground_truth.get("landing")
            ),
        }

        return errors

    except Exception as e:
        click.echo(f"Error processing {video_path}: {e}", err=True)
        return {
            "standing_end_error": float("nan"),
            "lowest_point_error": float("nan"),
            "takeoff_error": float("nan"),
            "landing_error": float("nan"),
        }


def evaluate_dropjump_detection(
    video_path: str,
    ground_truth: dict[str, float],
    fps: float,
    **params: Any,
) -> dict[str, float]:
    """
    Evaluate drop jump detection on a single video.

    Returns dict with errors for each event in frames.
    """
    try:
        # Run analysis with custom parameters
        result = process_dropjump_video(video_path, **params)

        if result is None:
            return {
                "drop_start_error": float("nan"),
                "landing_error": float("nan"),
                "takeoff_error": float("nan"),
            }

        # Convert to dict and extract data
        result_dict = result.to_dict()
        data = result_dict["data"]
        metadata = result_dict["metadata"]

        # Extract drop_start from metadata
        drop_start_frame = None
        if "algorithm" in metadata and "drop_detection" in metadata["algorithm"]:
            drop_start_frame = metadata["algorithm"]["drop_detection"].get("detected_drop_frame")

        # Map drop jump fields to ground truth events
        errors = {
            "drop_start_error": compute_frame_error(
                drop_start_frame, ground_truth.get("drop_start")
            ),
            "landing_error": compute_frame_error(
                data.get("contact_start_frame_precise"), ground_truth.get("landing")
            ),
            "takeoff_error": compute_frame_error(
                data.get("contact_end_frame_precise"), ground_truth.get("takeoff")
            ),
        }

        return errors

    except Exception as e:
        click.echo(f"Error processing {video_path}: {e}", err=True)
        return {
            "drop_start_error": float("nan"),
            "landing_error": float("nan"),
            "takeoff_error": float("nan"),
        }


def evaluate_all(ground_truth_data: dict[str, Any], **params: Any) -> dict[str, Any]:
    """
    Evaluate detection on all videos in ground truth dataset.

    Returns comprehensive evaluation metrics.
    """
    annotations = ground_truth_data["annotations"]

    cmj_errors: list[dict[str, float]] = []
    dj_errors: list[dict[str, float]] = []

    for annotation in annotations:
        video_file = annotation["video_file"]
        jump_type = annotation["jump_type"]
        fps = annotation.get("fps", 60.0)  # Default to 60fps if not specified
        gt = annotation["ground_truth"]

        # Skip if ground truth is not complete
        if any(v is None for v in gt.values()):
            click.echo(f"Skipping {video_file} - incomplete ground truth", err=True)
            continue

        if jump_type == "cmj":
            errors = evaluate_cmj_detection(video_file, gt, fps, **params)
            cmj_errors.append(errors)
        elif jump_type == "dropjump":
            errors = evaluate_dropjump_detection(video_file, gt, fps, **params)
            dj_errors.append(errors)

    # Compute aggregate statistics
    def aggregate_errors(errors: list[dict[str, float]]) -> dict[str, dict[str, float]]:
        if not errors:
            return {}

        result = {}
        for key in errors[0].keys():
            values = [e[key] for e in errors if not np.isnan(e[key])]
            if values:
                result[key] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "max": float(np.max(values)),
                    "median": float(np.median(values)),
                    "count": len(values),
                }
            else:
                result[key] = {
                    "mean": float("nan"),
                    "std": float("nan"),
                    "max": float("nan"),
                    "median": float("nan"),
                    "count": 0,
                }
        return result

    return {
        "cmj": {
            "errors": cmj_errors,
            "aggregate": aggregate_errors(cmj_errors),
        },
        "dropjump": {
            "errors": dj_errors,
            "aggregate": aggregate_errors(dj_errors),
        },
    }


@click.group()
def cli() -> None:
    """Parameter optimization for jump detection algorithms."""
    pass


@cli.command()
@click.option(
    "--ground-truth",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to ground truth annotations JSON",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Path to save evaluation results (JSON)",
)
def evaluate(ground_truth: Path, output: Path | None) -> None:
    """Evaluate current detection parameters against ground truth."""
    click.echo(f"Loading ground truth from: {ground_truth}")
    gt_data = load_ground_truth(ground_truth)

    click.echo("Evaluating current parameters...")
    results = evaluate_all(gt_data)

    # Print summary
    click.echo("\n" + "=" * 60)
    click.echo("CMJ Detection Errors (frames)")
    click.echo("=" * 60)
    for event, stats in results["cmj"]["aggregate"].items():
        event_name = event.replace("_error", "")
        click.echo(f"{event_name:20} | Mean: {stats['mean']:.2f} ± {stats['std']:.2f} "
                   f"| Max: {stats['max']:.2f} | Median: {stats['median']:.2f}")

    click.echo("\n" + "=" * 60)
    click.echo("Drop Jump Detection Errors (frames)")
    click.echo("=" * 60)
    for event, stats in results["dropjump"]["aggregate"].items():
        event_name = event.replace("_error", "")
        click.echo(f"{event_name:20} | Mean: {stats['mean']:.2f} ± {stats['std']:.2f} "
                   f"| Max: {stats['max']:.2f} | Median: {stats['median']:.2f}")

    # Compute overall MAE
    all_cmj_errors = [
        e for errors in results["cmj"]["errors"]
        for e in errors.values() if not np.isnan(e)
    ]
    all_dj_errors = [
        e for errors in results["dropjump"]["errors"]
        for e in errors.values() if not np.isnan(e)
    ]

    overall_mae = np.mean(all_cmj_errors + all_dj_errors) if (all_cmj_errors or all_dj_errors) else float("nan")

    click.echo(f"\nOverall MAE: {overall_mae:.2f} frames ({overall_mae/60*1000:.1f} ms at 60fps)")

    # Save results if requested
    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        click.echo(f"\nResults saved to: {output}")


@cli.command()
@click.option(
    "--ground-truth",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to ground truth annotations JSON",
)
@click.option(
    "--method",
    type=click.Choice(["grid", "scipy", "manual"]),
    default="grid",
    help="Optimization method",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Path to save optimized parameters (JSON)",
)
def optimize(ground_truth: Path, method: str, output: Path | None) -> None:
    """Optimize detection parameters using ground truth."""
    click.echo(f"Loading ground truth from: {ground_truth}")
    gt_data = load_ground_truth(ground_truth)

    if method == "grid":
        click.echo("\nRunning grid search optimization...")
        click.echo("This will test multiple parameter combinations.\n")

        # TODO: Implement grid search
        # Define parameter ranges
        # Test all combinations
        # Report best parameters

        click.echo("Grid search not yet implemented. Coming soon!")

    elif method == "scipy":
        click.echo("\nRunning scipy.optimize minimization...")

        # TODO: Implement scipy optimization
        # Define objective function (MAE)
        # Use scipy.optimize.minimize
        # Report best parameters

        click.echo("Scipy optimization not yet implemented. Coming soon!")

    else:
        click.echo("Manual optimization: Adjust parameters in params.json, then use 'test' command")


@cli.command()
@click.option(
    "--ground-truth",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to ground truth annotations JSON",
)
@click.option(
    "--params",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to parameter configuration JSON",
)
def test(ground_truth: Path, params: Path) -> None:
    """Test custom parameters against ground truth."""
    click.echo(f"Loading ground truth from: {ground_truth}")
    gt_data = load_ground_truth(ground_truth)

    click.echo(f"Loading parameters from: {params}")
    with open(params) as f:
        custom_params = json.load(f)

    click.echo("Testing custom parameters...")
    results = evaluate_all(gt_data, **custom_params)

    # Print summary (same as evaluate command)
    click.echo("\nResults with custom parameters:")
    click.echo("=" * 60)

    # Compute overall MAE
    all_cmj_errors = [
        e for errors in results["cmj"]["errors"]
        for e in errors.values() if not np.isnan(e)
    ]
    all_dj_errors = [
        e for errors in results["dropjump"]["errors"]
        for e in errors.values() if not np.isnan(e)
    ]

    overall_mae = np.mean(all_cmj_errors + all_dj_errors) if (all_cmj_errors or all_dj_errors) else float("nan")

    click.echo(f"Overall MAE: {overall_mae:.2f} frames ({overall_mae/60*1000:.1f} ms at 60fps)")


if __name__ == "__main__":
    cli()
