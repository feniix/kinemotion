"""Performance benchmark comparing MediaPipe vs RTMPose pose estimation.

Measures FPS, latency, and resource usage for pose tracking on test videos.
"""

from __future__ import annotations

import argparse
import json
import statistics

# Import RTMPoseTracker from same directory
import sys
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

import cv2

from kinemotion.core.pose import PoseTracker
from kinemotion.core.timing import PerformanceTimer

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rtmpose_tracker import RTMPoseTracker

# Test videos provided for benchmarking
TEST_VIDEOS = {
    "cmj": [
        "/Users/feniix/src/personal/cursor/kinemotion/samples/test-videos/cmj-45-IMG_6733.mp4",
        "/Users/feniix/src/personal/cursor/kinemotion/samples/test-videos/cmj-45-IMG_6734.mp4",
        "/Users/feniix/src/personal/cursor/kinemotion/samples/test-videos/cmj-45-IMG_6735.mp4",
    ],
    "dj": [
        "/Users/feniix/src/personal/cursor/kinemotion/samples/test-videos/dj-45-IMG_6739.mp4",
        "/Users/feniix/src/personal/cursor/kinemotion/samples/test-videos/dj-45-IMG_6740.mp4",
        "/Users/feniix/src/personal/cursor/kinemotion/samples/test-videos/dj-45-IMG_6741.mp4",
    ],
}


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    tracker_name: str
    mode: str
    video_path: str
    total_frames: int
    successful_frames: int
    total_time: float
    fps: float
    avg_frame_time: float
    min_frame_time: float
    max_frame_time: float
    std_frame_time: float
    initialization_time: float
    frame_times: list[float] = field(default_factory=list)
    timing_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "tracker": self.tracker_name,
            "mode": self.mode,
            "video": Path(self.video_path).name,
            "total_frames": self.total_frames,
            "successful_frames": self.successful_frames,
            "success_rate": self.successful_frames / self.total_frames
            if self.total_frames > 0
            else 0,
            "total_time": round(self.total_time, 3),
            "fps": round(self.fps, 2),
            "avg_frame_time_ms": round(self.avg_frame_time * 1000, 2),
            "min_frame_time_ms": round(self.min_frame_time * 1000, 2),
            "max_frame_time_ms": round(self.max_frame_time * 1000, 2),
            "std_frame_time_ms": round(self.std_frame_time * 1000, 2),
            "initialization_time_ms": round(self.initialization_time * 1000, 2),
            "timing_breakdown": {k: round(v * 1000, 2) for k, v in self.timing_breakdown.items()},
        }


def benchmark_tracker(
    tracker_name: str,
    tracker_factory,
    video_path: str,
    warmup_frames: int = 5,
    mode: str = "default",
) -> BenchmarkResult:
    """Benchmark a single tracker on a video.

    Args:
        tracker_name: Name of the tracker (for reporting)
        tracker_factory: Function that creates the tracker instance
        video_path: Path to test video
        warmup_frames: Number of frames to skip for warmup

    Returns:
        BenchmarkResult with metrics
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Measure initialization time
    init_start = perf_counter()
    timer = PerformanceTimer()
    tracker = tracker_factory(timer=timer)
    init_time = perf_counter() - init_start

    # Warmup
    frame_times = []
    for _ in range(warmup_frames):
        ret, frame = cap.read()
        if not ret:
            break
        tracker.process_frame(frame)

    # Reset timer for actual benchmark
    timer = PerformanceTimer()
    tracker = tracker_factory(timer=timer)

    # Benchmark loop
    successful_frames = 0
    start_time = perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_start = perf_counter()
        result = tracker.process_frame(frame)
        frame_time = perf_counter() - frame_start

        frame_times.append(frame_time)
        if result is not None:
            successful_frames += 1

    total_time = perf_counter() - start_time
    cap.release()
    tracker.close()

    # Calculate statistics
    avg_time = statistics.mean(frame_times) if frame_times else 0
    min_time = min(frame_times) if frame_times else 0
    max_time = max(frame_times) if frame_times else 0
    std_time = statistics.stdev(frame_times) if len(frame_times) > 1 else 0
    fps = len(frame_times) / total_time if total_time > 0 else 0

    # Get timing breakdown
    metrics = timer.get_metrics()

    return BenchmarkResult(
        tracker_name=tracker_name,
        mode=mode,
        video_path=video_path,
        total_frames=len(frame_times),
        successful_frames=successful_frames,
        total_time=total_time,
        fps=fps,
        avg_frame_time=avg_time,
        min_frame_time=min_time,
        max_frame_time=max_time,
        std_frame_time=std_time,
        initialization_time=init_time,
        frame_times=frame_times,
        timing_breakdown=metrics,
    )


def run_comparative_benchmark(
    categories: list[str] | None = None,
    output: str | None = None,
) -> dict[str, list[BenchmarkResult]]:
    """Run comparative benchmark across all configurations.

    Args:
        categories: List of video categories to test ('cmj', 'dj')
        output: Optional JSON output path

    Returns:
        Dictionary mapping tracker names to results
    """
    if categories is None:
        categories = ["cmj", "dj"]

    results: dict[str, list[BenchmarkResult]] = {
        "MediaPipe": [],
        "RTMPose-Lightweight-CPU": [],
        "RTMPose-Lightweight-CoreML": [],
        "RTMPose-Balanced-CPU": [],
        "RTMPose-Balanced-CoreML": [],
    }

    all_videos = []
    for cat in categories:
        all_videos.extend(TEST_VIDEOS.get(cat, []))

    print("=== Phase 2: Performance Assessment ===")
    print(f"Testing {len(all_videos)} videos across {len(results)} configurations")
    print()

    for video_path in all_videos:
        video_name = Path(video_path).name
        print(f"--- {video_name} ---")

        # Benchmark MediaPipe (use image mode to avoid timestamp issues)
        print("  MediaPipe...", end="", flush=True)
        result_mp = benchmark_tracker(
            "MediaPipe",
            lambda timer: PoseTracker(timer=timer, strategy="image"),
            video_path,
            mode="default",
        )
        results["MediaPipe"].append(result_mp)
        print(f" {result_mp.fps:.1f} FPS")

        # Benchmark RTMPose Lightweight CPU
        print("  RTMPose-Lightweight (CPU)...", end="", flush=True)
        result_rt_light_cpu = benchmark_tracker(
            "RTMPose-Lightweight-CPU",
            lambda timer: RTMPoseTracker(mode="lightweight", device="cpu", timer=timer),
            video_path,
            mode="lightweight",
        )
        results["RTMPose-Lightweight-CPU"].append(result_rt_light_cpu)
        print(f" {result_rt_light_cpu.fps:.1f} FPS")

        # Benchmark RTMPose Lightweight CoreML
        print("  RTMPose-Lightweight (CoreML)...", end="", flush=True)
        result_rt_light_coreml = benchmark_tracker(
            "RTMPose-Lightweight-CoreML",
            lambda timer: RTMPoseTracker(mode="lightweight", device="mps", timer=timer),
            video_path,
            mode="lightweight",
        )
        results["RTMPose-Lightweight-CoreML"].append(result_rt_light_coreml)
        print(f" {result_rt_light_coreml.fps:.1f} FPS")

        # Benchmark RTMPose Balanced CPU
        print("  RTMPose-Balanced (CPU)...", end="", flush=True)
        result_rt_balanced_cpu = benchmark_tracker(
            "RTMPose-Balanced-CPU",
            lambda timer: RTMPoseTracker(mode="balanced", device="cpu", timer=timer),
            video_path,
            mode="balanced",
        )
        results["RTMPose-Balanced-CPU"].append(result_rt_balanced_cpu)
        print(f" {result_rt_balanced_cpu.fps:.1f} FPS")

        # Benchmark RTMPose Balanced CoreML
        print("  RTMPose-Balanced (CoreML)...", end="", flush=True)
        result_rt_balanced_coreml = benchmark_tracker(
            "RTMPose-Balanced-CoreML",
            lambda timer: RTMPoseTracker(mode="balanced", device="mps", timer=timer),
            video_path,
            mode="balanced",
        )
        results["RTMPose-Balanced-CoreML"].append(result_rt_balanced_coreml)
        print(f" {result_rt_balanced_coreml.fps:.1f} FPS")
        print()

    # Output results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable format
        output_data = {
            tracker: [r.to_dict() for r in results_list]
            for tracker, results_list in results.items()
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {output_path}")

    return results


def print_summary(results: dict[str, list[BenchmarkResult]]) -> None:
    """Print summary statistics for all trackers."""
    print()
    print("=== Performance Summary ===")
    print()
    print(f"{'Tracker':<20} {'Avg FPS':<10} {'Avg Frame (ms)':<15} {'Std (ms)':<10}")
    print("-" * 60)

    for tracker_name, results_list in results.items():
        if not results_list:
            continue

        avg_fps = statistics.mean([r.fps for r in results_list])
        avg_frame = statistics.mean([r.avg_frame_time * 1000 for r in results_list])
        std_frame = statistics.mean([r.std_frame_time * 1000 for r in results_list])

        print(f"{tracker_name:<20} {avg_fps:<10.2f} {avg_frame:<15.2f} {std_frame:<10.2f}")

    print()
    print("=== Success Rate ===")
    print()
    print(f"{'Tracker':<20} {'Success Rate':<15}")
    print("-" * 40)

    for tracker_name, results_list in results.items():
        if not results_list:
            continue

        total_frames = sum(r.total_frames for r in results_list)
        successful_frames = sum(r.successful_frames for r in results_list)
        success_rate = (successful_frames / total_frames * 100) if total_frames > 0 else 0

        print(f"{tracker_name:<20} {success_rate:<15.1f}%")


def main():
    """Main entry point for benchmark script."""
    parser = argparse.ArgumentParser(description="Benchmark MediaPipe vs RTMPose performance")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["cmj", "dj"],
        choices=["cmj", "dj"],
        help="Video categories to benchmark",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    results = run_comparative_benchmark(
        categories=args.categories,
        output=args.output,
    )

    print_summary(results)

    # Calculate performance vs MediaPipe
    print()
    print("=== Performance vs MediaPipe ===")
    print()

    mp_avg_fps = statistics.mean([r.fps for r in results["MediaPipe"]])

    for tracker_name, results_list in results.items():
        if tracker_name == "MediaPipe" or not results_list:
            continue

        avg_fps = statistics.mean([r.fps for r in results_list])
        ratio = (avg_fps / mp_avg_fps * 100) if mp_avg_fps > 0 else 0
        status = "✅" if ratio >= 80 else "⚠️" if ratio >= 50 else "❌"
        print(f"{tracker_name}: {ratio:.1f}% of MediaPipe FPS {status}")


if __name__ == "__main__":
    main()
