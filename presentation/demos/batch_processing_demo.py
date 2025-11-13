#!/usr/bin/env python3
"""
Batch Processing Demo for Kinemotion Presentation

This script demonstrates how to process multiple drop jump videos in parallel
using Kinemotion's bulk processing API.

Usage:
    python batch_processing_demo.py

Requirements:
    - kinemotion installed: pip install kinemotion
    - Sample drop jump videos in ./sample_videos/ directory
"""

import json
import time
import warnings
from pathlib import Path

# Suppress protobuf deprecation warnings from MediaPipe
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk  # noqa: E402


def main():
    """Run batch processing demo."""

    print("=" * 60)
    print("Kinemotion Batch Processing Demo")
    print("=" * 60)
    print()

    # Setup
    video_dir = Path("sample_data")
    output_dir = Path("batch_results")
    output_dir.mkdir(exist_ok=True)

    # Find all video files (mp4, mov, avi)
    video_files = []
    for ext in ["*.mp4", "*.MP4", "*.mov", "*.MOV", "*.avi", "*.AVI"]:
        video_files.extend(video_dir.glob(ext))

    if not video_files:
        print(f"⚠️  No videos found in {video_dir}/")
        print("Please add some sample videos first.")
        return

    print(f"📹 Found {len(video_files)} videos to process")
    print()

    # List videos
    for i, video in enumerate(video_files, 1):
        print(f"  {i}. {video.name}")
    print()

    # Process with different worker counts to show performance
    worker_counts = [1, 4]

    for workers in worker_counts:
        print(f"🚀 Processing with {workers} worker(s)...")
        print("-" * 60)

        start_time = time.time()

        try:
            # Create configs for each video
            configs = [
                DropJumpVideoConfig(video_path=str(v), quality="balanced")
                for v in video_files
            ]

            # Bulk process all videos
            results = process_dropjump_videos_bulk(configs=configs, max_workers=workers)

            elapsed = time.time() - start_time

            # Show results
            print(f"✅ Processed {len(results)} videos in {elapsed:.2f} seconds")
            print(f"   Average: {elapsed/len(results):.2f} seconds per video")
            print()

            # Show sample metrics
            if results:
                print("📊 Sample Results:")
                for result in results[:3]:
                    video_name = Path(result.video_path).name
                    if not result.success or not result.metrics:
                        error_msg = result.error or "Unknown error"
                        print(f"   ❌ {video_name}: {error_msg}")
                    else:
                        metrics = result.metrics
                        # Calculate RSI (jump height / ground contact time in seconds)
                        gct_seconds = (
                            metrics.ground_contact_time
                            if metrics.ground_contact_time
                            else 0
                        )
                        rsi = (
                            (metrics.jump_height / gct_seconds)
                            if (gct_seconds > 0 and metrics.jump_height)
                            else 0
                        )

                        print(f"   ✅ {video_name}:")
                        gct_ms = (
                            metrics.ground_contact_time * 1000
                            if metrics.ground_contact_time
                            else 0
                        )
                        ft_ms = metrics.flight_time * 1000 if metrics.flight_time else 0
                        jh_m = metrics.jump_height if metrics.jump_height else 0
                        print(f"      Ground Contact Time: {gct_ms:.0f}ms")
                        print(f"      Flight Time: {ft_ms:.0f}ms")
                        print(f"      Jump Height: {jh_m:.3f}m")
                        print(f"      RSI: {rsi:.2f}")
                print()

            # Save results to JSON
            output_file = output_dir / f"results_{workers}workers.json"
            results_dict = [
                {
                    "video_path": r.video_path,
                    "success": r.success,
                    "error": r.error,
                    "metrics": r.metrics.to_dict() if r.success and r.metrics else None,
                    "processing_time": r.processing_time,
                }
                for r in results
            ]
            with open(output_file, "w") as f:
                json.dump(results_dict, f, indent=2)
            print(f"💾 Results saved to: {output_file}")
            print()

        except Exception as e:
            print(f"❌ Error: {e}")
            print()

    # Show performance comparison
    print("=" * 60)
    print("🎯 Key Takeaways:")
    print("=" * 60)
    print()
    print("✅ Parallel processing significantly speeds up batch analysis")
    print("✅ Perfect for team assessments (process entire team at once)")
    print("✅ Results exported to JSON for further analysis")
    print("✅ Error handling per video (one failure doesn't stop batch)")
    print()
    print("📁 Check batch_results/ directory for JSON output")
    print()


if __name__ == "__main__":
    main()
