#!/usr/bin/env python3
"""
Simple example: Process a single video or multiple videos using kinemotion.

This demonstrates the most straightforward way to use kinemotion as a library.
"""

from kinemotion.api import (
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_video,
    process_dropjump_videos_bulk,
)


def process_single_video_example() -> None:
    """Process a single video - the simplest usage."""
    print("Processing single video...")

    # Process with just the video path
    metrics = process_dropjump_video(
        video_path="my_video.mp4",
        verbose=True,
    )

    # Print results
    if metrics.ground_contact_time:
        print(f"\nGround contact time: {metrics.ground_contact_time * 1000:.1f} ms")
    if metrics.flight_time:
        print(f"Flight time: {metrics.flight_time * 1000:.1f} ms")
    if metrics.jump_height:
        print(
            f"Jump height: {metrics.jump_height:.3f} m ({metrics.jump_height * 100:.1f} cm)"
        )


def process_multiple_videos_example() -> None:
    """Process multiple videos in parallel."""
    print("\nProcessing multiple videos in parallel...")

    # Configure videos to process
    configs = [
        DropJumpVideoConfig("athlete1_jump1.mp4"),
        DropJumpVideoConfig("athlete1_jump2.mp4"),
        DropJumpVideoConfig("athlete1_jump3.mp4"),
        DropJumpVideoConfig("athlete2_jump1.mp4", quality="accurate"),
    ]

    # Process all videos using 4 parallel workers
    # Progress callback shows completion status
    def show_progress(result: DropJumpVideoResult) -> None:
        if result.success:
            print(f"✓ {result.video_path} - {result.processing_time:.1f}s")
        else:
            print(f"✗ {result.video_path} - ERROR: {result.error}")

    results = process_dropjump_videos_bulk(
        configs, max_workers=4, progress_callback=show_progress
    )

    # Calculate statistics
    successful = [
        r
        for r in results
        if r.success and r.metrics and r.metrics.jump_height is not None
    ]
    if successful:
        # Type narrowing: we know metrics and jump_height exist for all items
        avg_jump = sum(
            r.metrics.jump_height
            for r in successful  # type: ignore[union-attr,misc]
        ) / len(successful)
        print(f"\nAverage jump height: {avg_jump:.3f} m ({avg_jump * 100:.1f} cm)")


def process_with_outputs_example() -> None:
    """Process video and save debug video + JSON results."""
    print("\nProcessing with output files...")

    metrics = process_dropjump_video(
        video_path="my_video.mp4",
        output_video="debug_output.mp4",  # Save annotated video
        json_output="results.json",  # Save metrics as JSON
        quality="accurate",  # Use highest quality analysis
        verbose=True,
    )

    if metrics.jump_height:
        print(f"Jump height: {metrics.jump_height:.3f} m")
    print("Debug video saved to: debug_output.mp4")
    print("Metrics saved to: results.json")


if __name__ == "__main__":
    print("Edit this script to run examples:")
    print("  - process_single_video_example()")
    print("  - process_multiple_videos_example()")
    print("  - process_with_outputs_example()")
