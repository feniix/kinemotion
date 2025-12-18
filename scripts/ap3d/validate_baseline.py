#!/usr/bin/env python3
"""
Baseline validation script for AthletePose3D.
Runs validation on the test split and generates a report.
"""

import logging
from pathlib import Path

import click
from scripts.ap3d.ap3d_validator import AP3DValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

@click.command()
@click.option("--ap3d-root", type=click.Path(exists=True, path_type=Path), default="data/athletepose3d", help="Root directory of AP3D dataset")
@click.option("--split", type=str, default="test", help="Split to validate (train, validation, test)")
@click.option("--output-report", type=click.Path(path_type=Path), default="reports/ap3d_baseline_validation.md", help="Path to save validation report")
def main(ap3d_root: Path, split: str, output_report: Path) -> None:
    """Run baseline validation on AP3D dataset."""
    logger.info(f"Starting AP3D validation on '{split}' split...")

    try:
        validator = AP3DValidator(ap3d_root)
        summary = validator.validate_split(split)

        if not summary:
            logger.error(f"No results found for split '{split}'.")
            return

        # Ensure reports directory exists
        output_report.parent.mkdir(parents=True, exist_ok=True)

        validator.generate_report(summary, output_report)

        logger.info("Validation complete!")
        logger.info(f"Mean MPJPE: {summary.get('mean_mpjpe'):.2f} px")
        logger.info(f"Report saved to: {output_report}")

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
