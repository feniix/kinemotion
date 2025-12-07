#!/usr/bin/env python3
"""
Helper script to prepare ground truth template with video metadata.

This script scans validation videos and pre-fills FPS and frame count information.

Usage:
    python scripts/prepare_ground_truth.py --video-dir samples/validation --output samples/validation/ground_truth.json
"""

import json
from pathlib import Path

import click
import cv2


def extract_video_metadata(video_path: Path) -> dict[str, float]:
    """Extract FPS and frame count from video."""
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cap.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration_seconds": frame_count / fps if fps > 0 else 0,
    }


@click.command()
@click.option(
    "--video-dir",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Directory containing validation videos",
)
@click.option(
    "--template",
    type=click.Path(exists=True, path_type=Path),
    default="samples/validation/ground_truth_template.json",
    help="Path to ground truth template",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default="samples/validation/ground_truth.json",
    help="Path to save prepared ground truth file",
)
def main(video_dir: Path, template: Path, output: Path) -> None:
    """Prepare ground truth file with video metadata."""
    click.echo(f"Loading template from: {template}")

    with open(template) as f:
        data = json.load(f)

    click.echo(f"Scanning videos in: {video_dir}\n")

    for annotation in data["annotations"]:
        video_file = annotation["video_file"]
        video_path = Path(video_file)

        if not video_path.exists():
            click.echo(f"⚠️  Video not found: {video_file}", err=True)
            continue

        try:
            metadata = extract_video_metadata(video_path)
            annotation["fps"] = metadata["fps"]
            annotation["frame_count"] = metadata["frame_count"]
            annotation["duration_seconds"] = metadata["duration_seconds"]

            click.echo(
                f"✓ {video_path.name:30} | {metadata['fps']:.1f} fps | "
                f"{metadata['frame_count']} frames | {metadata['duration_seconds']:.1f}s"
            )

        except Exception as e:
            click.echo(f"✗ {video_path.name}: {e}", err=True)

    # Save prepared file
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(data, f, indent=2)

    click.echo(f"\n✓ Ground truth template saved to: {output}")
    click.echo("\nNext steps:")
    click.echo("1. Watch the debug videos and note frame numbers for key events")
    click.echo("2. Fill in the ground_truth fields in the JSON file")
    click.echo("3. Run: python scripts/optimize_detection_params.py evaluate --ground-truth samples/validation/ground_truth.json")


if __name__ == "__main__":
    main()
