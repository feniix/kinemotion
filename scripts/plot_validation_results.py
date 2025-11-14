#!/usr/bin/env python3
"""Create visualizations for known height validation results.

Generates:
1. Scatter plot: measured vs theoretical flight times
2. Residual plot: showing error distribution
3. Bland-Altman plot: agreement analysis
"""

import json
import sys
from pathlib import Path

import numpy as np


def plot_measured_vs_theoretical(
    results_json: Path, output_path: Path | None = None
) -> None:
    """Create scatter plot comparing measured vs theoretical flight times.

    Args:
        results_json: Path to results.json from validate_known_heights.py
        output_path: Path to save plot (default: validation_measured_vs_theoretical.png)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Skipping visualization.")
        print("Install with: pip install matplotlib")
        return

    with open(results_json) as f:
        data = json.load(f)

    results = data["results"]

    if not results:
        print("No results to plot")
        return

    measured = np.array([r["measured_flight_time_s"] for r in results])
    theoretical = np.array([r["theoretical_flight_time_s"] for r in results])
    heights = np.array([r["true_height_m"] for r in results])

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))

    # Scatter plot colored by height
    colors = {"0.5": "#FF6B6B", "1.0": "#4ECDC4", "1.5": "#45B7D1"}
    height_colors = [colors.get(str(h), "#999999") for h in heights]

    ax.scatter(
        theoretical,
        measured,
        s=100,
        alpha=0.7,
        c=height_colors,
        edgecolors="black",
        linewidth=1,
    )

    # Perfect agreement line
    min_val = min(theoretical.min(), measured.min()) * 0.95
    max_val = max(theoretical.max(), measured.max()) * 1.05
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        "k--",
        alpha=0.5,
        linewidth=2,
        label="Perfect agreement",
    )

    # Fit line
    coeffs = np.polyfit(theoretical, measured, 1)
    fit_line = coeffs[0] * theoretical + coeffs[1]
    ax.plot(
        theoretical,
        fit_line,
        "r-",
        linewidth=2,
        label=f"Fit: y={coeffs[0]:.3f}x+{coeffs[1]:.4f}",
    )

    # Labels and formatting
    ax.set_xlabel("Theoretical Flight Time (s)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Measured Flight Time (s)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Known Height Validation: Measured vs Theoretical Flight Times",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)

    # Legend
    correlation = np.corrcoef(theoretical, measured)[0, 1]

    # Add colored markers to legend
    from matplotlib.patches import Patch

    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            linestyle="--",
            color="k",
            alpha=0.5,
            linewidth=2,
            label="Perfect agreement",
        ),
        plt.Line2D(
            [0],
            [0],
            color="r",
            linewidth=2,
            label=f"Fit: y={coeffs[0]:.3f}x+{coeffs[1]:.4f}",
        ),
        Patch(facecolor="#FF6B6B", edgecolor="black", label="0.5m drops"),
        Patch(facecolor="#4ECDC4", edgecolor="black", label="1.0m drops"),
        Patch(facecolor="#45B7D1", edgecolor="black", label="1.5m drops"),
    ]

    ax.legend(handles=legend_elements, loc="upper left", fontsize=10)
    ax.text(
        0.95,
        0.05,
        f"r = {correlation:.6f}",
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="bottom",
        horizontalalignment="right",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
    )

    plt.tight_layout()

    if output_path is None:
        output_path = Path("validation_measured_vs_theoretical.png")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def plot_residuals(results_json: Path, output_path: Path | None = None) -> None:
    """Create residual plot showing error distribution.

    Args:
        results_json: Path to results.json from validate_known_heights.py
        output_path: Path to save plot (default: validation_residuals.png)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Skipping visualization.")
        return

    with open(results_json) as f:
        data = json.load(f)

    results = data["results"]
    summary = data["summary"]

    if not results:
        print("No results to plot")
        return

    theoretical = np.array([r["theoretical_flight_time_s"] for r in results])
    errors_ms = np.array([r["absolute_error_ms"] for r in results])

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Residual scatter plot
    ax1.scatter(
        theoretical, errors_ms, s=100, alpha=0.7, edgecolors="black", linewidth=1
    )
    ax1.axhline(y=0, color="k", linestyle="--", linewidth=2, label="Zero error")
    ax1.axhline(
        y=summary["bias_ms"],
        color="r",
        linestyle="-",
        linewidth=2,
        label=f"Bias: {summary['bias_ms']:.2f}ms",
    )

    # Add confidence bands
    std = summary["std_ms"]
    ax1.fill_between(
        [theoretical.min(), theoretical.max()],
        -1.96 * std,
        1.96 * std,
        alpha=0.2,
        color="blue",
        label=f"±1.96σ ({1.96*std:.2f}ms)",
    )

    ax1.set_xlabel("Theoretical Flight Time (s)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Absolute Error (ms)", fontsize=12, fontweight="bold")
    ax1.set_title("Residuals: Measured - Theoretical", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # Right: Error distribution histogram
    ax2.hist(errors_ms, bins=10, alpha=0.7, edgecolor="black", color="steelblue")
    ax2.axvline(
        x=summary["bias_ms"],
        color="r",
        linestyle="-",
        linewidth=2,
        label=f"Mean: {summary['bias_ms']:.2f}ms",
    )
    ax2.axvline(
        x=summary["bias_ms"] + summary["std_ms"],
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"±1σ: {summary['std_ms']:.2f}ms",
    )
    ax2.axvline(
        x=summary["bias_ms"] - summary["std_ms"],
        color="orange",
        linestyle="--",
        linewidth=2,
    )

    ax2.set_xlabel("Absolute Error (ms)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Frequency", fontsize=12, fontweight="bold")
    ax2.set_title("Error Distribution", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if output_path is None:
        output_path = Path("validation_residuals.png")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def plot_bland_altman(results_json: Path, output_path: Path | None = None) -> None:
    """Create Bland-Altman plot for agreement analysis.

    Args:
        results_json: Path to results.json from validate_known_heights.py
        output_path: Path to save plot (default: validation_bland_altman.png)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Skipping visualization.")
        return

    with open(results_json) as f:
        data = json.load(f)

    results = data["results"]
    summary = data["summary"]

    if not results:
        print("No results to plot")
        return

    measured = np.array([r["measured_flight_time_s"] for r in results])
    theoretical = np.array([r["theoretical_flight_time_s"] for r in results])

    # Calculate Bland-Altman values
    mean_times = (measured + theoretical) / 2
    differences_ms = (measured - theoretical) * 1000

    # Calculate limits of agreement
    mean_diff = np.mean(differences_ms)
    std_diff = np.std(differences_ms)
    upper_limit = mean_diff + 1.96 * std_diff
    lower_limit = mean_diff - 1.96 * std_diff

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 7))

    ax.scatter(
        mean_times, differences_ms, s=100, alpha=0.7, edgecolors="black", linewidth=1
    )

    # Mean difference line
    ax.axhline(
        y=mean_diff,
        color="r",
        linestyle="-",
        linewidth=2,
        label=f"Mean diff: {mean_diff:.2f}ms",
    )

    # Limits of agreement
    ax.axhline(
        y=upper_limit,
        color="b",
        linestyle="--",
        linewidth=2,
        label=f"Upper LoA: +{upper_limit:.2f}ms",
    )
    ax.axhline(
        y=lower_limit,
        color="b",
        linestyle="--",
        linewidth=2,
        label=f"Lower LoA: {lower_limit:.2f}ms",
    )

    # Fill between limits
    ax.fill_between(mean_times, lower_limit, upper_limit, alpha=0.1, color="blue")

    ax.set_xlabel("Mean Flight Time (s)", fontsize=12, fontweight="bold")
    ax.set_ylabel(
        "Difference: Measured - Theoretical (ms)", fontsize=12, fontweight="bold"
    )
    ax.set_title(
        "Bland-Altman Plot: Agreement Analysis", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # Add statistics box
    stats_text = f"""MAE: {summary['mae_ms']:.2f}ms
RMSE: {summary['rmse_ms']:.2f}ms
r: {summary['correlation']:.6f}"""

    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.8},
        family="monospace",
    )

    plt.tight_layout()

    if output_path is None:
        output_path = Path("validation_bland_altman.png")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def create_all_plots(results_json: Path, output_dir: Path | None = None) -> None:
    """Create all validation plots.

    Args:
        results_json: Path to results.json from validate_known_heights.py
        output_dir: Directory to save plots (default: current directory)
    """
    if output_dir is None:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating validation plots in {output_dir}...")
    print()

    plot_measured_vs_theoretical(
        results_json, output_dir / "validation_measured_vs_theoretical.png"
    )
    plot_residuals(results_json, output_dir / "validation_residuals.png")
    plot_bland_altman(results_json, output_dir / "validation_bland_altman.png")

    print()
    print("All plots created successfully!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create visualizations for known height validation results",
        epilog="Requires: results.json from validate_known_heights.py",
    )

    parser.add_argument(
        "results_json",
        type=Path,
        help="Path to results.json from validate_known_heights.py",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory to save plots (default: current directory)",
    )

    parser.add_argument(
        "--type",
        choices=["all", "scatter", "residuals", "bland-altman"],
        default="all",
        help="Which plots to create (default: all)",
    )

    args = parser.parse_args()

    if not args.results_json.exists():
        print(f"Error: {args.results_json} not found", file=sys.stderr)
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.type == "all":
            create_all_plots(args.results_json, args.output_dir)
        elif args.type == "scatter":
            plot_measured_vs_theoretical(
                args.results_json,
                args.output_dir / "validation_measured_vs_theoretical.png",
            )
        elif args.type == "residuals":
            plot_residuals(
                args.results_json, args.output_dir / "validation_residuals.png"
            )
        elif args.type == "bland-altman":
            plot_bland_altman(
                args.results_json, args.output_dir / "validation_bland_altman.png"
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
