#!/usr/bin/env python3
"""
Example: Bulk video processing using kinemotion as a library.

This script demonstrates how to process multiple drop jump videos in parallel
using the kinemotion API for high-throughput analysis.
"""

from pathlib import Path

from kinemotion.api import (
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_videos_bulk,
)


def example_simple_bulk() -> None:
    """Example 1: Simple bulk processing with default settings."""
    print("=" * 80)
    print("EXAMPLE 1: Simple Bulk Processing")
    print("=" * 80)

    video_configs = [
        DropJumpVideoConfig(video_path="video1.mp4"),
        DropJumpVideoConfig(video_path="video2.mp4"),
        DropJumpVideoConfig(video_path="video3.mp4"),
    ]

    # Process videos with 4 parallel workers
    results = process_dropjump_videos_bulk(video_configs, max_workers=4)

    # Print results
    for result in results:
        print_result(result)


def example_advanced_configuration() -> None:
    """Example 2: Advanced configuration with different quality settings."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Advanced Configuration")
    print("=" * 80)

    advanced_configs = [
        # Fast analysis for quick screening
        DropJumpVideoConfig(
            video_path="athlete1_trial1.mp4",
            quality="fast",
            json_output="results/athlete1_trial1.json",
        ),
        # Balanced analysis (default)
        DropJumpVideoConfig(
            video_path="athlete1_trial2.mp4",
            quality="balanced",
            json_output="results/athlete1_trial2.json",
        ),
        # Research-grade accurate analysis with debug video
        DropJumpVideoConfig(
            video_path="athlete1_trial3.mp4",
            quality="accurate",
            output_video="debug/athlete1_trial3_debug.mp4",
            json_output="results/athlete1_trial3.json",
        ),
    ]

    # Create output directories
    Path("results").mkdir(exist_ok=True)
    Path("debug").mkdir(exist_ok=True)

    # Progress callback to show completion
    def on_progress(result: DropJumpVideoResult) -> None:
        status = "✓" if result.success else "✗"
        print(
            f"{status} Completed: {result.video_path} ({result.processing_time:.2f}s)"
        )

    process_dropjump_videos_bulk(
        advanced_configs, max_workers=2, progress_callback=on_progress
    )


def example_process_directory() -> list[DropJumpVideoResult]:
    """Example 3: Process entire directory with consistent settings."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Process Directory")
    print("=" * 80)

    # Progress callback to show completion
    def on_progress(result: DropJumpVideoResult) -> None:
        status = "✓" if result.success else "✗"
        print(
            f"{status} Completed: {result.video_path} ({result.processing_time:.2f}s)"
        )

    # Find all MP4 files in a directory
    video_dir = Path("videos")
    if not video_dir.exists():
        print("Directory 'videos' not found - skipping")
        return []

    video_files = list(video_dir.glob("*.mp4"))

    # Create configs with same drop height for all
    dir_configs = [
        DropJumpVideoConfig(
            video_path=str(video_file),
            quality="balanced",
            json_output=f"results/{video_file.stem}.json",
        )
        for video_file in video_files
    ]

    print(f"Found {len(video_files)} videos to process")

    results = process_dropjump_videos_bulk(
        dir_configs, max_workers=4, progress_callback=on_progress
    )

    print_summary(results)
    return results


def example_export_csv(results: list[DropJumpVideoResult]) -> None:
    """Example 4: Export results to CSV."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Export to CSV")
    print("=" * 80)

    # Collect successful results
    successful_results = [r for r in results if r.success]

    if not successful_results:
        print("No successful results to export")
        return

    import csv

    output_csv = "results/analysis_summary.csv"

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "Video",
                "Ground Contact Time (ms)",
                "Flight Time (ms)",
                "Jump Height (m)",
                "Processing Time (s)",
            ]
        )

        # Data rows
        for result in successful_results:
            assert result.metrics is not None
            writer.writerow(
                [
                    Path(result.video_path).name,
                    (
                        f"{result.metrics.ground_contact_time * 1000:.1f}"
                        if result.metrics.ground_contact_time
                        else "N/A"
                    ),
                    (
                        f"{result.metrics.flight_time * 1000:.1f}"
                        if result.metrics.flight_time
                        else "N/A"
                    ),
                    (
                        f"{result.metrics.jump_height:.3f}"
                        if result.metrics.jump_height
                        else "N/A"
                    ),
                    f"{result.processing_time:.2f}",
                ]
            )

    print(f"Results exported to: {output_csv}")


def example_custom_parameters() -> None:
    """Example 5: Process with custom parameters for challenging videos."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom Parameters for Low-Quality Videos")
    print("=" * 80)

    custom_configs = [
        # Low quality video - use more aggressive smoothing
        DropJumpVideoConfig(
            video_path="low_quality.mp4",
            smoothing_window=7,  # More smoothing
            velocity_threshold=0.025,  # Higher threshold
            quality="accurate",
        ),
        # High speed video - adjust for higher framerate
        DropJumpVideoConfig(
            video_path="high_speed_120fps.mp4",
            quality="accurate",
            # Auto-tuning will handle FPS adjustments
        ),
    ]

    # Progress callback to show completion
    def on_progress(result: DropJumpVideoResult) -> None:
        status = "✓" if result.success else "✗"
        print(
            f"{status} Completed: {result.video_path} ({result.processing_time:.2f}s)"
        )

    # Process with custom settings
    process_dropjump_videos_bulk(
        custom_configs, max_workers=2, progress_callback=on_progress
    )


def print_result(result: DropJumpVideoResult) -> None:
    """Print a single video processing result."""
    if result.success:
        assert result.metrics is not None
        print(f"\n✓ {result.video_path} ({result.processing_time:.2f}s)")
        if result.metrics.ground_contact_time:
            print(
                f"  Ground contact time: {result.metrics.ground_contact_time * 1000:.1f} ms"
            )
        if result.metrics.flight_time:
            print(f"  Flight time: {result.metrics.flight_time * 1000:.1f} ms")
        if result.metrics.jump_height:
            print(f"  Jump height: {result.metrics.jump_height:.3f} m")
    else:
        print(f"\n✗ {result.video_path} - FAILED")
        print(f"  Error: {result.error}")


def print_summary(results: list[DropJumpVideoResult]) -> None:
    """Print summary statistics for a batch of results."""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total videos: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if not successful:
        return

    # Filter for non-None metrics
    with_gct = [
        r for r in successful if r.metrics and r.metrics.ground_contact_time is not None
    ]
    with_jump = [
        r for r in successful if r.metrics and r.metrics.jump_height is not None
    ]

    if with_gct:
        # Type narrowing: we know metrics and ground_contact_time exist
        avg_gct = sum(
            r.metrics.ground_contact_time * 1000  # type: ignore[union-attr,operator,misc]
            for r in with_gct
        ) / len(with_gct)
        print(f"\nAverage ground contact time: {avg_gct:.1f} ms")

    if with_jump:
        # Type narrowing: we know metrics and jump_height exist
        avg_jump = sum(
            r.metrics.jump_height
            for r in with_jump  # type: ignore[union-attr,misc]
        ) / len(with_jump)
        print(f"Average jump height: {avg_jump:.3f} m")


def main() -> None:
    """Process multiple videos in parallel and save results."""
    example_simple_bulk()
    example_advanced_configuration()
    results = example_process_directory()
    example_export_csv(results)
    example_custom_parameters()


def example_single_video() -> None:
    """Example: Process a single video programmatically."""
    from kinemotion.api import process_dropjump_video

    print("\n" + "=" * 80)
    print("SINGLE VIDEO PROCESSING")
    print("=" * 80)

    try:
        # Process single video with verbose output
        metrics = process_dropjump_video(
            video_path="sample.mp4",
            quality="balanced",
            output_video="sample_debug.mp4",
            json_output="sample_results.json",
            verbose=True,
        )

        # Access metrics directly
        print("\nResults:")
        if metrics.ground_contact_time:
            print(f"Ground contact time: {metrics.ground_contact_time * 1000:.1f} ms")
        if metrics.flight_time:
            print(f"Flight time: {metrics.flight_time * 1000:.1f} ms")
        if metrics.jump_height:
            print(f"Jump height: {metrics.jump_height:.3f} m")

        # Access raw data
        if metrics.contact_start_frame:
            print(f"\nContact start frame: {metrics.contact_start_frame}")
        if metrics.contact_end_frame:
            print(f"Takeoff frame: {metrics.contact_end_frame}")
        if metrics.flight_end_frame:
            print(f"Landing frame: {metrics.flight_end_frame}")

    except FileNotFoundError:
        print("Sample video not found - skipping single video example")
    except Exception as e:
        print(f"Error processing video: {e}")


if __name__ == "__main__":
    # Run examples
    example_single_video()
    main()
