#!/usr/bin/env python3
"""Analyze variance in determinism test results.

This script provides detailed statistical analysis of the 100 runs
to detect any subtle non-determinism or floating point variance.
"""

import json
import sys
from pathlib import Path

import numpy as np


def extract_metric(data: dict, path: list[str]):
    """Extract nested metric from data dict."""
    current = data
    for key in path:
        if key not in current:
            return None
        current = current[key]
    return current


def analyze_variability(results_dir: Path) -> bool:
    """Analyze variability in metrics across all runs.

    Returns:
        True if deterministic (zero or negligible variance), False otherwise
    """
    json_files = sorted(results_dir.glob("test_*.json"))

    if len(json_files) < 2:
        print(f"Error: Only found {len(json_files)} result files")
        return False

    print(f"Analyzing variability across {len(json_files)} runs...")
    print("=" * 70)

    # DATA metrics (should be deterministic)
    data_metrics = [
        (["data", "jump_height_m"], "Jump Height (m)", True),
        (["data", "flight_time_s"], "Flight Time (s)", True),
        (["data", "takeoff_frame"], "Takeoff Frame", True),
        (["data", "landing_frame"], "Landing Frame", True),
        (["data", "countermovement_depth_m"], "Countermovement Depth (m)", True),
        (["data", "eccentric_duration_s"], "Eccentric Duration (s)", True),
        (["data", "concentric_duration_s"], "Concentric Duration (s)", True),
    ]

    # METADATA metrics (quality should be deterministic, processing may vary)
    metadata_metrics = [
        (["metadata", "quality", "score"], "Quality Score", True),
        (
            ["metadata", "quality", "indicators", "avg_visibility"],
            "Avg Visibility",
            True,
        ),
        (["metadata", "quality", "indicators", "outliers_detected"], "Outliers", True),
        (["metadata", "processing", "processing_time_s"], "Processing Time (s)", False),
    ]

    all_deterministic = True

    print("\n📊 DATA METRICS (should be deterministic):")
    print("-" * 70)

    for metric_path, metric_name, _ in data_metrics:
        # Extract metric from all runs
        values = []
        for file in json_files:
            with open(file) as f:
                data = json.load(f)
            value = extract_metric(data, metric_path)
            if value is not None:
                values.append(value)

        if not values:
            print(f"\n{metric_name}: N/A (not found)")
            continue

        values = np.array(values)

        # Calculate statistics
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        range_val = max_val - min_val

        print(f"\n{metric_name}:")
        print(f"  Mean:  {mean_val:.10f}")
        print(f"  Std:   {std_val:.15f}")
        print(f"  Min:   {min_val:.10f}")
        print(f"  Max:   {max_val:.10f}")
        print(f"  Range: {range_val:.15f}")

        # Assess determinism (all data metrics should be deterministic)
        if std_val == 0 and range_val == 0:
            print("  ✅ PERFECT: Zero variance (perfectly deterministic)")
        elif std_val < 1e-10:
            print("  ✅ ACCEPTABLE: Tiny variance (floating point precision only)")
        elif std_val < 1e-6:
            print("  ⚠️  WARNING: Small variance (investigate)")
            all_deterministic = False
        else:
            print("  ❌ FAILED: Significant variance (non-deterministic!)")
            all_deterministic = False

    print("\n📈 METADATA METRICS:")
    print("-" * 70)

    for metric_path, metric_name, should_be_deterministic in metadata_metrics:
        # Extract metric from all runs
        values = []
        for file in json_files:
            with open(file) as f:
                data = json.load(f)
            value = extract_metric(data, metric_path)
            if value is not None:
                values.append(value)

        if not values:
            print(f"\n{metric_name}: N/A (not found)")
            continue

        values = np.array(values)

        # Calculate statistics
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        range_val = max_val - min_val

        print(f"\n{metric_name}:")
        print(f"  Mean:  {mean_val:.10f}")
        print(f"  Std:   {std_val:.15f}")
        print(f"  Range: {range_val:.15f}")

        # Assess
        if should_be_deterministic:
            # Quality metrics should be deterministic
            if std_val == 0:
                print("  ✅ PERFECT: Deterministic quality metric")
            elif std_val < 1e-10:
                print("  ✅ ACCEPTABLE: Tiny variance")
            else:
                print("  ⚠️  WARNING: Quality metric varies (unexpected)")
                all_deterministic = False
        else:
            # Processing time, timestamp should vary
            if std_val > 0:
                print("  ℹ️  VARIES: As expected (system/time dependent)")
            else:
                print("  ⚠️  NOTE: Unexpectedly constant")

    # Final verdict
    print("\n" + "=" * 70)
    if all_deterministic:
        print("✅ DETERMINISM TEST PASSED")
        print("\nAll measurements are deterministic (zero or negligible variance)")
        print("Algorithm produces identical results for identical inputs")
        return True
    else:
        print("❌ DETERMINISM TEST FAILED")
        print("\nSome metrics show non-deterministic behavior")
        print("Investigation required before proceeding with validation")
        return False


if __name__ == "__main__":
    results_dir = Path("data/determinism_test/results")

    if not results_dir.exists():
        print("Error: Results directory not found")
        print("Run ./scripts/test_determinism.sh first")
        sys.exit(1)

    success = analyze_variability(results_dir)
    sys.exit(0 if success else 1)
