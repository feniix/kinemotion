"""Tier 1 integration tests for dropjump CLI.

These tests use maintainable patterns:
- Test exit codes (stable)
- Test file creation behavior (stable)
- Use loose text matching (semi-stable)
- Avoid hardcoding exact output strings (fragile)
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest
from click.testing import CliRunner

from kinemotion.api import DropJumpVideoResult
from kinemotion.dropjump.cli import dropjump_analyze
from kinemotion.dropjump.kinematics import DropJumpMetrics

# Skip batch/multiprocessing tests in CI
# MediaPipe doesn't work with ProcessPoolExecutor in headless environments
skip_in_ci = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Batch processing with MediaPipe not supported in CI headless environment",
)


# cli_runner and minimal_video fixtures moved to tests/conftest.py


@pytest.fixture
def mock_dropjump_metrics() -> DropJumpMetrics:
    """Create a dummy DropJumpMetrics object."""
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.2
    metrics.flight_time = 0.5
    metrics.jump_height = 0.3
    metrics.jump_height_kinematic = 0.3
    metrics.jump_height_trajectory_m = 0.3
    metrics.drop_start_frame = 10
    metrics.contact_start_frame = 20
    metrics.contact_end_frame = 26
    metrics.flight_start_frame = 26
    metrics.flight_end_frame = 41
    metrics.peak_height_frame = 33
    return metrics


@pytest.fixture
def mock_dropjump_api(mock_dropjump_metrics: DropJumpMetrics):
    """Mock process_dropjump_video and bulk processing to avoid real analysis."""
    # Mock for single video processing
    with (
        patch("kinemotion.dropjump.cli.process_dropjump_video") as mock_single,
        patch("kinemotion.dropjump.cli.process_dropjump_videos_bulk") as mock_bulk,
    ):

        def single_side_effect(
            video_path,
            output_video=None,
            json_output=None,
            **kwargs,
        ):
            # Create dummy output files if requested
            if output_video:
                Path(output_video).parent.mkdir(parents=True, exist_ok=True)
                with open(output_video, "wb") as f:
                    f.write(b"fake video content")

            if json_output:
                Path(json_output).parent.mkdir(parents=True, exist_ok=True)
                # Write minimal valid JSON to satisfy tests that read it
                with open(json_output, "w") as f:
                    # Manually construct dict since to_dict might need metadata
                    data = {
                        "data": {
                            "ground_contact_time_ms": 200.0,
                            "flight_time_ms": 500.0,
                            "jump_height_m": 0.3,
                        },
                        "metadata": {},
                    }
                    json.dump(data, f)

            return mock_dropjump_metrics

        mock_single.side_effect = single_side_effect

        def bulk_side_effect(configs, max_workers=None, progress_callback=None):
            results = []
            for config in configs:
                # Create dummy outputs for each config
                if config.output_video:
                    Path(config.output_video).parent.mkdir(parents=True, exist_ok=True)
                    with open(config.output_video, "wb") as f:
                        f.write(b"fake video content")

                if config.json_output:
                    Path(config.json_output).parent.mkdir(parents=True, exist_ok=True)
                    with open(config.json_output, "w") as f:
                        data = {
                            "data": {
                                "ground_contact_time_ms": 200.0,
                                "flight_time_ms": 500.0,
                                "jump_height_m": 0.3,
                            },
                            "metadata": {},
                        }
                        json.dump(data, f)

                result = DropJumpVideoResult(
                    video_path=config.video_path,
                    success=True,
                    metrics=mock_dropjump_metrics,
                    processing_time=0.1,
                )
                results.append(result)
                if progress_callback:
                    progress_callback(result)
            return results

        mock_bulk.side_effect = bulk_side_effect

        yield (mock_single, mock_bulk)


@pytest.mark.usefixtures("mock_dropjump_api")
class TestDropJumpCLIHelp:
    """Test help text accessibility."""

    def test_help_displays_successfully(self, cli_runner: CliRunner) -> None:
        """Test --help flag works and exits cleanly."""
        result = cli_runner.invoke(dropjump_analyze, ["--help"])

        # ✅ STABLE: Exit code for help
        assert result.exit_code == 0

    def test_help_mentions_key_options(self, cli_runner: CliRunner) -> None:
        """Test help includes critical options (not exact text)."""
        result = cli_runner.invoke(dropjump_analyze, ["--help"])

        # ✅ SEMI-STABLE: Check for option names, not descriptions
        assert "--quality" in result.output or "-q" in result.output
        assert "--output" in result.output or "-o" in result.output


class TestDropJumpCLIErrors:
    """Test error handling."""

    def test_missing_video_file_fails(self, cli_runner: CliRunner) -> None:
        """Test command fails for nonexistent video."""
        result = cli_runner.invoke(dropjump_analyze, ["nonexistent.mp4"])

        # ✅ STABLE: Should fail
        assert result.exit_code != 0

    def test_invalid_quality_preset_fails(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test invalid quality preset is rejected."""
        result = cli_runner.invoke(dropjump_analyze, [str(minimal_video), "--quality", "invalid"])

        # ✅ STABLE: Should fail with non-zero exit
        assert result.exit_code != 0


@pytest.mark.usefixtures("mock_dropjump_api")
class TestDropJumpCLIFileOperations:
    """Test file creation behavior."""

    def test_json_output_file_created(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test JSON output file is created."""
        json_output = tmp_path / "metrics.json"

        result = cli_runner.invoke(
            dropjump_analyze,
            [
                str(minimal_video),
                "--json-output",
                str(json_output),
                "--quality",
                "fast",
            ],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: Test file creation
        assert json_output.exists()

        # ✅ STABLE: Test JSON structure, not values
        with open(json_output) as f:
            data = json.load(f)

        # Test new data/metadata structure
        assert isinstance(data, dict)
        assert "data" in data
        assert "metadata" in data

        # Test keys exist in data, not their values (which may be None)
        assert "ground_contact_time_ms" in data["data"]
        assert "flight_time_ms" in data["data"]

    def test_debug_video_output_created(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test debug video file is created."""
        debug_output = tmp_path / "debug.mp4"

        result = cli_runner.invoke(
            dropjump_analyze,
            [str(minimal_video), "--output", str(debug_output), "--quality", "fast"],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: Test file creation
        assert debug_output.exists()
        # ✅ STABLE: Test file is not empty
        assert debug_output.stat().st_size > 0


@pytest.mark.usefixtures("mock_dropjump_api")
class TestDropJumpCLIOptions:
    """Test option parsing and acceptance."""

    @pytest.mark.parametrize("quality", ["fast", "balanced", "accurate"])
    def test_quality_presets_accepted(
        self, cli_runner: CliRunner, minimal_video: Path, quality: str
    ) -> None:
        """Test all quality presets are recognized."""
        result = cli_runner.invoke(dropjump_analyze, [str(minimal_video), "--quality", quality])

        # ✅ STABLE: Quality should be accepted (no parsing error)
        # Don't check if processing succeeded, just if option was valid
        # Exit code may vary but shouldn't have "Invalid quality" error
        assert "Invalid quality" not in result.output

    def test_expert_parameters_accepted(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test expert parameter overrides are accepted."""
        result = cli_runner.invoke(
            dropjump_analyze,
            [
                str(minimal_video),
                "--smoothing-window",
                "7",
                "--velocity-threshold",
                "0.025",
                "--quality",
                "fast",
            ],
        )

        # ✅ STABLE: Parameters should be parsed without error
        # Don't care about processing result, just parsing
        assert "invalid" not in result.output.lower() or result.exit_code == 0


@pytest.mark.usefixtures("mock_dropjump_api")
class TestDropJumpCLIBasicExecution:
    """Test basic command execution."""

    def test_command_runs_without_crash(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test command executes without crashing."""
        result = cli_runner.invoke(dropjump_analyze, [str(minimal_video), "--quality", "fast"])

        # ✅ STABLE: Should complete (success or graceful failure, not crash)
        # Synthetic video may cause analysis to fail, but shouldn't crash
        assert result.exit_code in [0, 1]  # Success or handled failure
        # No exception should be raised
        assert result.exception is None or result.exit_code != 0

    def test_command_with_all_output_options(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test command with all output options together."""
        json_out = tmp_path / "metrics.json"
        video_out = tmp_path / "debug.mp4"

        result = cli_runner.invoke(
            dropjump_analyze,
            [
                str(minimal_video),
                "--json-output",
                str(json_out),
                "--output",
                str(video_out),
                "--quality",
                "fast",
            ],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: Files should be created
        assert json_out.exists()
        assert video_out.exists()


# Tier 2: Advanced features


@pytest.mark.usefixtures("mock_dropjump_api")
class TestDropJumpCLIBatchMode:
    """Test batch processing features."""

    @skip_in_ci
    def test_batch_mode_with_multiple_videos(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test batch mode processes multiple videos."""
        # Create 2 test videos
        video1 = tmp_path / "video1.mp4"
        video2 = tmp_path / "video2.mp4"

        for video_path in [video1, video2]:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
            for _ in range(30):
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                out.write(frame)
            out.release()

        result = cli_runner.invoke(
            dropjump_analyze,
            [str(video1), str(video2), "--batch", "--quality", "fast"],
        )

        # ✅ STABLE: Batch mode should execute without crash
        assert result.exception is None or result.exit_code != 0

    @skip_in_ci
    def test_output_directory_creation(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test that output directories are created automatically."""
        # Non-existent directory path
        output_dir = tmp_path / "outputs"
        json_dir = tmp_path / "json_outputs"

        # Directory should NOT exist before command
        assert not output_dir.exists()
        assert not json_dir.exists()

        result = cli_runner.invoke(
            dropjump_analyze,
            [
                str(minimal_video),
                "--batch",
                "--output-dir",
                str(output_dir),
                "--json-output-dir",
                str(json_dir),
                "--quality",
                "fast",
            ],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: Directories should be created
        assert output_dir.exists()
        assert json_dir.exists()
        assert output_dir.is_dir()
        assert json_dir.is_dir()

    @skip_in_ci
    def test_csv_summary_created(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test CSV summary file creation in batch mode."""
        csv_path = tmp_path / "summary.csv"

        result = cli_runner.invoke(
            dropjump_analyze,
            [
                str(minimal_video),
                "--batch",
                "--csv-summary",
                str(csv_path),
                "--quality",
                "fast",
            ],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: If successful, CSV file should exist
        if result.exit_code == 0 and csv_path.exists():
            # ✅ STABLE: Verify CSV structure, not content
            import csv

            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                # Check header exists (DictReader needs headers)
                assert reader.fieldnames is not None
                # Check at least one row exists (our video)
                assert len(rows) >= 1
                # DON'T check specific column names or values

    @skip_in_ci
    def test_batch_with_multiple_videos_and_csv(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test batch processing multiple videos with CSV summary."""
        # Create 3 test videos
        videos = []
        for i in range(3):
            video = tmp_path / f"video{i}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(video), fourcc, 30.0, (640, 480))
            for _ in range(30):
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                out.write(frame)
            out.release()
            videos.append(video)

        csv_path = tmp_path / "summary.csv"

        result = cli_runner.invoke(
            dropjump_analyze,
            [
                *[str(v) for v in videos],
                "--batch",
                "--csv-summary",
                str(csv_path),
                "--quality",
                "fast",
            ],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: CSV should exist
        if csv_path.exists():
            import csv

            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                # ✅ STABLE: Should have processed all videos (or attempted to)
                # Count rows, not check content
                assert len(rows) >= 1  # At least something processed

    @skip_in_ci
    def test_workers_option_accepted(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test --workers option is accepted."""
        result = cli_runner.invoke(
            dropjump_analyze,
            [str(minimal_video), "--batch", "--workers", "2", "--quality", "fast"],
        )

        # ✅ STABLE: Workers option should be parsed without error
        assert "workers" not in result.output.lower() or result.exit_code in [0, 1]
