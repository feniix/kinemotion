#!/usr/bin/env python3
"""
Debug script to compare detected events vs ground truth for each video.

Shows detailed breakdown of errors to identify algorithm failure modes.
"""

import json
import sys
from pathlib import Path

import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kinemotion.api import process_cmj_video, process_dropjump_video


def load_ground_truth(filepath: Path) -> dict:
    """Load ground truth annotations from JSON file."""
    with open(filepath) as f:
        return json.load(f)


@click.group()
def cli() -> None:
    """Debug detection algorithms."""
    pass


@cli.command()
@click.option(
    "--ground-truth",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to ground truth annotations JSON",
)
def dropjump(ground_truth: Path) -> None:
    """Debug drop jump detection for each video."""
    gt_data = load_ground_truth(ground_truth)

    click.echo("=" * 80)
    click.echo("DROP JUMP DETECTION DEBUG")
    click.echo("=" * 80)

    dj_videos = [a for a in gt_data["annotations"] if a["jump_type"] == "dropjump"]

    for i, annotation in enumerate(dj_videos, 1):
        video_file = annotation["video_file"]
        gt = annotation["ground_truth"]
        fps = annotation["fps"]

        click.echo(f"\n{'=' * 80}")
        click.echo(f"VIDEO {i}/3: {Path(video_file).name}")
        click.echo(f"{'=' * 80}")

        try:
            # Run analysis
            result = process_dropjump_video(video_file)

            if result is None:
                click.echo("❌ Analysis failed - result is None")
                continue

            # Convert to dict
            result_dict = result.to_dict()
            data = result_dict["data"]
            metadata = result_dict["metadata"]

            # Extract detected events
            drop_start_detected = None
            if "algorithm" in metadata and "drop_detection" in metadata["algorithm"]:
                drop_start_detected = metadata["algorithm"]["drop_detection"].get("detected_drop_frame")

            landing_detected = data.get("contact_start_frame_precise")
            takeoff_detected = data.get("contact_end_frame_precise")

            # Ground truth
            drop_start_gt = gt.get("drop_start")
            landing_gt = gt.get("landing")
            takeoff_gt = gt.get("takeoff")

            # Calculate errors
            drop_error = abs(drop_start_detected - drop_start_gt) if drop_start_detected and drop_start_gt else None
            landing_error = abs(landing_detected - landing_gt) if landing_detected and landing_gt else None
            takeoff_error = abs(takeoff_detected - takeoff_gt) if takeoff_detected and takeoff_gt else None

            # Display comparison table
            click.echo(f"\n{'Event':<20} | {'Ground Truth':>15} | {'Detected':>15} | {'Error':>10} | Status")
            click.echo("-" * 80)

            # Drop start
            status = "✅" if drop_error and drop_error <= 5 else ("⚠️ NULL" if drop_error is None else "❌")
            detected_str = str(drop_start_detected) if drop_start_detected is not None else "NULL"
            error_str = f"{drop_error:.1f}f" if drop_error is not None else "N/A"
            click.echo(
                f"{'drop_start':<20} | {drop_start_gt:>15} | {detected_str:>15} | "
                f"{error_str:>10} | {status}"
            )

            # Landing
            status = "✅" if landing_error and landing_error <= 5 else ("⚠️ NULL" if landing_error is None else "❌")
            detected_str = f"{landing_detected:.1f}" if landing_detected is not None else "NULL"
            error_str = f"{landing_error:.1f}f" if landing_error is not None else "N/A"
            click.echo(
                f"{'landing':<20} | {landing_gt:>15} | {detected_str:>15} | "
                f"{error_str:>10} | {status}"
            )

            # Takeoff
            status = "✅" if takeoff_error and takeoff_error <= 5 else ("⚠️ NULL" if takeoff_error is None else "❌")
            detected_str = f"{takeoff_detected:.1f}" if takeoff_detected is not None else "NULL"
            error_str = f"{takeoff_error:.1f}f" if takeoff_error is not None else "N/A"
            click.echo(
                f"{'takeoff':<20} | {takeoff_gt:>15} | {detected_str:>15} | "
                f"{error_str:>10} | {status}"
            )

            # Convert to milliseconds
            click.echo(f"\n📊 Error Summary (@ {fps:.1f} fps):")
            if drop_error:
                click.echo(f"  • drop_start: {drop_error:.1f} frames = {drop_error/fps*1000:.1f}ms")
            if landing_error:
                click.echo(f"  • landing: {landing_error:.1f} frames = {landing_error/fps*1000:.1f}ms")
            if takeoff_error:
                click.echo(f"  • takeoff: {takeoff_error:.1f} frames = {takeoff_error/fps*1000:.1f}ms")

            # Additional debug info
            click.echo(f"\n🔍 Additional Info:")
            click.echo(f"  • Total frames: {annotation.get('frame_count')}")
            click.echo(f"  • Video duration: {annotation.get('duration_seconds'):.2f}s")
            click.echo(f"  • Ground contact time: {data.get('ground_contact_time_ms'):.1f}ms")
            click.echo(f"  • Flight time: {data.get('flight_time_ms'):.1f}ms")

            # Check if phases make sense
            if landing_detected and takeoff_detected:
                contact_duration = (takeoff_detected - landing_detected) / fps * 1000
                click.echo(f"  • Detected contact duration: {contact_duration:.1f}ms")

                gt_contact_duration = (takeoff_gt - landing_gt) / fps * 1000
                click.echo(f"  • Ground truth contact duration: {gt_contact_duration:.1f}ms")

        except Exception as e:
            click.echo(f"❌ Error processing: {e}")
            import traceback
            traceback.print_exc()


@cli.command()
@click.option(
    "--ground-truth",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to ground truth annotations JSON",
)
def cmj(ground_truth: Path) -> None:
    """Debug CMJ detection for each video."""
    gt_data = load_ground_truth(ground_truth)

    click.echo("=" * 80)
    click.echo("CMJ DETECTION DEBUG")
    click.echo("=" * 80)

    cmj_videos = [a for a in gt_data["annotations"] if a["jump_type"] == "cmj"]

    for i, annotation in enumerate(cmj_videos, 1):
        video_file = annotation["video_file"]
        gt = annotation["ground_truth"]
        fps = annotation["fps"]

        click.echo(f"\n{'=' * 80}")
        click.echo(f"VIDEO {i}/3: {Path(video_file).name}")
        click.echo(f"{'=' * 80}")

        try:
            # Run analysis
            result = process_cmj_video(video_file)

            if result is None:
                click.echo("❌ Analysis failed - result is None")
                continue

            # Convert to dict
            result_dict = result.to_dict()
            data = result_dict["data"]

            # Extract detected events
            standing_detected = data.get("standing_start_frame")
            lowest_detected = data.get("lowest_point_frame")
            takeoff_detected = data.get("takeoff_frame")
            landing_detected = data.get("landing_frame")

            # Ground truth
            standing_gt = gt.get("standing_end")
            lowest_gt = gt.get("lowest_point")
            takeoff_gt = gt.get("takeoff")
            landing_gt = gt.get("landing")

            # Calculate errors
            standing_error = abs(standing_detected - standing_gt) if standing_detected and standing_gt else None
            lowest_error = abs(lowest_detected - lowest_gt) if lowest_detected and lowest_gt else None
            takeoff_error = abs(takeoff_detected - takeoff_gt) if takeoff_detected and takeoff_gt else None
            landing_error = abs(landing_detected - landing_gt) if landing_detected and landing_gt else None

            # Display comparison table
            click.echo(f"\n{'Event':<20} | {'Ground Truth':>15} | {'Detected':>15} | {'Error':>10} | Status")
            click.echo("-" * 80)

            # Standing end
            status = "✅" if standing_error and standing_error <= 5 else "❌"
            click.echo(
                f"{'standing_end':<20} | {standing_gt:>15} | {standing_detected:>15.1f} | "
                f"{standing_error:>9.1f}f | {status}"
            )

            # Lowest point
            status = "✅" if lowest_error and lowest_error <= 5 else "❌"
            click.echo(
                f"{'lowest_point':<20} | {lowest_gt:>15} | {lowest_detected:>15.1f} | "
                f"{lowest_error:>9.1f}f | {status}"
            )

            # Takeoff
            status = "✅" if takeoff_error and takeoff_error <= 5 else "❌"
            click.echo(
                f"{'takeoff':<20} | {takeoff_gt:>15} | {takeoff_detected:>15.1f} | "
                f"{takeoff_error:>9.1f}f | {status}"
            )

            # Landing
            status = "✅" if landing_error and landing_error <= 5 else "❌"
            click.echo(
                f"{'landing':<20} | {landing_gt:>15} | {landing_detected:>15.1f} | "
                f"{landing_error:>9.1f}f | {status}"
            )

            # Convert to milliseconds
            click.echo(f"\n📊 Error Summary (@ {fps:.1f} fps):")
            if standing_error:
                click.echo(f"  • standing_end: {standing_error:.1f} frames = {standing_error/fps*1000:.1f}ms")
            if lowest_error:
                click.echo(f"  • lowest_point: {lowest_error:.1f} frames = {lowest_error/fps*1000:.1f}ms")
            if takeoff_error:
                click.echo(f"  • takeoff: {takeoff_error:.1f} frames = {takeoff_error/fps*1000:.1f}ms")
            if landing_error:
                click.echo(f"  • landing: {landing_error:.1f} frames = {landing_error/fps*1000:.1f}ms")

            # Additional debug info
            click.echo(f"\n🔍 Additional Info:")
            click.echo(f"  • Jump height: {data.get('jump_height_m'):.3f}m")
            click.echo(f"  • Flight time: {data.get('flight_time_ms'):.1f}ms")
            click.echo(f"  • Countermovement depth: {data.get('countermovement_depth_m'):.3f}m")

        except Exception as e:
            click.echo(f"❌ Error processing: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    cli()
