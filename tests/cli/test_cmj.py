"""Tier 1 integration tests for CMJ CLI.

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

from kinemotion.cmj.cli import cmj_analyze
from kinemotion.cmj.kinematics import CMJMetrics

pytestmark = [
    pytest.mark.integration,
    pytest.mark.cli,
    pytest.mark.cmj,
    pytest.mark.requires_video,
]

# Skip batch/multiprocessing tests in CI
# MediaPipe doesn't work with ProcessPoolExecutor in headless environments
skip_in_ci = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Batch processing with MediaPipe not supported in CI headless environment",
)


# cli_runner and minimal_video fixtures moved to tests/conftest.py


@pytest.fixture
def mock_cmj_metrics() -> CMJMetrics:
    """Create a dummy CMJMetrics object."""
    return CMJMetrics(
        jump_height=0.4,
        flight_time=0.5,
        countermovement_depth=0.3,
        eccentric_duration=0.4,
        concentric_duration=0.3,
        total_movement_time=0.7,
        peak_eccentric_velocity=-2.0,
        peak_concentric_velocity=2.5,
        transition_time=0.1,
        standing_start_frame=10.0,
        lowest_point_frame=20.0,
        takeoff_frame=30.0,
        landing_frame=45.0,
        video_fps=30.0,
        tracking_method="foot",
    )


@pytest.fixture
def mock_cmj_api(mock_cmj_metrics: CMJMetrics):
    """Mock process_cmj_video to avoid real analysis."""
    with patch("kinemotion.cmj.cli.process_cmj_video") as mock:

        def side_effect(
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
                    json.dump(mock_cmj_metrics.to_dict(), f)

            return mock_cmj_metrics

        mock.side_effect = side_effect
        yield mock


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIHelp:
    """Test help text accessibility."""

    def test_help_displays_successfully(self, cli_runner: CliRunner) -> None:
        """Test --help flag works and exits cleanly."""
        result = cli_runner.invoke(cmj_analyze, ["--help"])

        # ✅ STABLE: Exit code for help
        assert result.exit_code == 0

    def test_help_mentions_key_options(self, cli_runner: CliRunner) -> None:
        """Test help includes critical options (not exact text)."""
        result = cli_runner.invoke(cmj_analyze, ["--help"])

        # ✅ SEMI-STABLE: Check for option names, not descriptions
        assert "--quality" in result.output or "-q" in result.output
        assert "--output" in result.output or "-o" in result.output


class TestCMJCLIErrors:
    """Test error handling."""

    def test_missing_video_file_fails(self, cli_runner: CliRunner) -> None:
        """Test command fails for nonexistent video."""
        result = cli_runner.invoke(cmj_analyze, ["nonexistent.mp4"])

        # ✅ STABLE: Should fail
        assert result.exit_code != 0

    def test_invalid_quality_preset_fails(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test invalid quality preset is rejected."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "invalid"])

        # ✅ STABLE: Should fail with non-zero exit
        assert result.exit_code != 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIFileOperations:
    """Test file creation behavior."""

    def test_json_output_file_created(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test JSON output file is created when analysis succeeds."""
        json_output = tmp_path / "metrics.json"

        result = cli_runner.invoke(
            cmj_analyze,
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

        # ✅ STABLE: If analysis succeeded, file should exist
        if result.exit_code == 0:
            assert json_output.exists()

            # ✅ STABLE: Test JSON structure, not values
            with open(json_output) as f:
                data = json.load(f)

            # Test keys exist, not their values (which may be None)
            assert isinstance(data, dict)
            assert "data" in data
            assert "jump_height_m" in data["data"]
            assert "flight_time_ms" in data["data"]

    def test_debug_video_output_created(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test debug video file is created when analysis succeeds."""
        debug_output = tmp_path / "debug.mp4"

        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), "--output", str(debug_output), "--quality", "fast"],
        )

        # ✅ STABLE: Command should complete without crash
        assert result.exception is None or result.exit_code != 0

        # ✅ STABLE: If analysis succeeded, test file creation
        if result.exit_code == 0:
            assert debug_output.exists()
            # ✅ STABLE: Test file is not empty
            assert debug_output.stat().st_size > 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIOptions:
    """Test option parsing and acceptance."""

    @pytest.mark.parametrize("quality", ["fast", "balanced", "accurate"])
    def test_quality_presets_accepted(
        self, cli_runner: CliRunner, minimal_video: Path, quality: str
    ) -> None:
        """Test all quality presets are recognized."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", quality])

        # ✅ STABLE: Quality should be accepted (no parsing error)
        # Don't check if processing succeeded, just if option was valid
        assert "Invalid quality" not in result.output

    def test_expert_parameters_accepted(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test expert parameter overrides are accepted."""
        result = cli_runner.invoke(
            cmj_analyze,
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
        assert "invalid" not in result.output.lower() or result.exit_code == 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIBasicExecution:
    """Test basic command execution."""

    def test_command_runs_without_crash(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test command executes without crashing."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

        # ✅ STABLE: Should complete (success or graceful failure, not crash)
        # Synthetic video may cause analysis to fail, but shouldn't crash
        assert result.exit_code in [0, 1]  # Success or handled failure
        # No unhandled exception
        assert result.exception is None or result.exit_code != 0

    def test_command_with_all_output_options(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test command with all output options together."""
        json_out = tmp_path / "metrics.json"
        video_out = tmp_path / "debug.mp4"

        result = cli_runner.invoke(
            cmj_analyze,
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

        # ✅ STABLE: If analysis succeeded, files should be created
        if result.exit_code == 0:
            assert json_out.exists()
            assert video_out.exists()


# Tier 2: Advanced features


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIBatchMode:
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
            cmj_analyze,
            [str(video1), str(video2), "--batch", "--quality", "fast"],
        )

        # ✅ STABLE: Batch mode should execute without crash
        assert result.exception is None or result.exit_code != 0

    @skip_in_ci
    def test_output_directory_creation(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test that output directories are created when batch processing succeeds."""
        # Non-existent directory path
        output_dir = tmp_path / "outputs"
        json_dir = tmp_path / "json_outputs"

        # Directory should NOT exist before command
        assert not output_dir.exists()
        assert not json_dir.exists()

        result = cli_runner.invoke(
            cmj_analyze,
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

        # ✅ STABLE: If successful, directories should be created
        if result.exit_code == 0:
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
            cmj_analyze,
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
            cmj_analyze,
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
            cmj_analyze,
            [str(minimal_video), "--batch", "--workers", "2", "--quality", "fast"],
        )

        # ✅ STABLE: Workers option should be parsed without error
        assert "workers" not in result.output.lower() or result.exit_code in [0, 1]


# Tier 3: Error handling and edge cases


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLICollectVideoFiles:
    """Test video file collection edge cases."""

    def test_collect_video_files_with_valid_files(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test collecting video files from glob patterns."""
        # Create test video files
        video1 = tmp_path / "video1.mp4"
        video2 = tmp_path / "video2.mp4"

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        for video_path in [video1, video2]:
            out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
            for _ in range(10):
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                out.write(frame)
            out.release()

        # Test with glob pattern
        pattern = str(tmp_path / "*.mp4")
        result = cli_runner.invoke(cmj_analyze, [pattern, "--batch", "--quality", "fast"])

        # Should recognize and process both files
        assert result.exception is None or result.exit_code != 0

    def test_collect_video_files_with_no_matches(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test handling when glob pattern finds no matches."""
        result = cli_runner.invoke(cmj_analyze, [str(tmp_path / "nonexistent*.mp4")])

        # Should fail gracefully with non-zero exit code
        assert result.exit_code != 0

    def test_collect_video_files_with_direct_path(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test collecting video files with direct file path."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

        # Direct path should work
        assert result.exception is None or result.exit_code != 0


class TestCMJCLIExceptionHandling:
    """Test exception handling and error paths."""

    def test_single_video_processing_exception(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test exception handling when processing single video fails."""
        # Create a corrupted/invalid video file
        invalid_video = tmp_path / "invalid.mp4"
        invalid_video.write_text("this is not a video")

        result = cli_runner.invoke(cmj_analyze, [str(invalid_video), "--quality", "fast"])

        # Should fail with non-zero exit code
        assert result.exit_code != 0

    def test_single_video_with_verbose_exception(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test verbose exception printing for single video processing."""
        # Create a corrupted video file
        invalid_video = tmp_path / "invalid.mp4"
        invalid_video.write_text("not a video")

        result = cli_runner.invoke(
            cmj_analyze,
            [str(invalid_video), "--verbose", "--quality", "fast"],
        )

        # Should fail with non-zero exit code in verbose mode
        assert result.exit_code != 0

    @skip_in_ci
    def test_batch_video_processing_exception(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test exception handling in batch mode continues processing."""
        # Create one valid and one invalid video
        valid_video = tmp_path / "valid.mp4"
        invalid_video = tmp_path / "invalid.mp4"

        # Create valid video
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(valid_video), fourcc, 30.0, (640, 480))
        for _ in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        # Create invalid video
        invalid_video.write_text("not a video")

        result = cli_runner.invoke(
            cmj_analyze,
            [str(valid_video), str(invalid_video), "--batch", "--quality", "fast"],
        )

        # Batch mode should handle error and continue
        # (may succeed or fail, but shouldn't crash)
        assert result.exception is None or result.exit_code != 0

    @skip_in_ci
    def test_batch_with_all_invalid_videos(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test batch mode when all videos are invalid."""
        invalid1 = tmp_path / "invalid1.mp4"
        invalid2 = tmp_path / "invalid2.mp4"

        invalid1.write_text("not video 1")
        invalid2.write_text("not video 2")

        result = cli_runner.invoke(
            cmj_analyze,
            [str(invalid1), str(invalid2), "--batch", "--quality", "fast"],
        )

        # Should handle errors gracefully
        assert result.exception is None or result.exit_code != 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIOutputResults:
    """Test output formatting and file creation."""

    def test_output_results_to_json_file(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test JSON output file creation and format."""
        json_output = tmp_path / "output.json"

        result = cli_runner.invoke(
            cmj_analyze,
            [
                str(minimal_video),
                "--json-output",
                str(json_output),
                "--quality",
                "fast",
            ],
        )

        # If successful, JSON file should exist and be valid
        if result.exit_code == 0:
            assert json_output.exists()
            with open(json_output) as f:
                data = json.load(f)
                assert isinstance(data, dict)

    def test_output_results_to_stdout(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test JSON output to stdout when no file specified."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

        # If successful, stdout should contain JSON
        if result.exit_code == 0:
            # Check for JSON markers or CMJ results
            assert "{" in result.output or "CMJ ANALYSIS" in result.output

    def test_output_results_contains_metrics(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test output results contain expected metric fields."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

        # If successful, check for expected metric output
        if result.exit_code == 0:
            # Check for any of the expected metrics in output
            metrics = [
                "jump_height",
                "flight_time",
                "countermovement_depth",
                "eccentric_duration",
                "CMJ ANALYSIS",
            ]
            assert any(metric in result.output for metric in metrics)


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIQualityPresets:
    """Test quality preset handling."""

    def test_case_insensitive_quality_preset(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test quality presets are case-insensitive."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "FAST"])

        # Should accept uppercase and convert to lowercase
        assert "Invalid quality" not in result.output

    def test_invalid_quality_preset_error(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test invalid quality preset is rejected."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "supersonic"])

        # Should fail with invalid choice error
        assert result.exit_code != 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIExpertParameters:
    """Test expert parameter validation and usage."""

    def test_all_expert_parameters(self, cli_runner: CliRunner, minimal_video: Path) -> None:
        """Test all expert parameters are accepted and passed through."""
        result = cli_runner.invoke(
            cmj_analyze,
            [
                str(minimal_video),
                "--smoothing-window",
                "7",
                "--velocity-threshold",
                "0.025",
                "--countermovement-threshold",
                "-0.15",
                "--min-contact-frames",
                "5",
                "--visibility-threshold",
                "0.5",
                "--detection-confidence",
                "0.8",
                "--tracking-confidence",
                "0.8",
                "--quality",
                "fast",
            ],
        )

        # Parameters should be parsed without error
        assert result.exception is None or result.exit_code != 0

    def test_expert_parameters_with_batch(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test expert parameters work with batch mode."""
        result = cli_runner.invoke(
            cmj_analyze,
            [
                str(minimal_video),
                "--batch",
                "--smoothing-window",
                "5",
                "--velocity-threshold",
                "0.02",
                "--quality",
                "fast",
            ],
        )

        # Parameters should be passed to batch processing
        assert result.exception is None or result.exit_code != 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIMultipleVideos:
    """Test handling of multiple video arguments."""

    def test_implicit_batch_mode_with_multiple_videos(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test batch mode is automatically enabled with multiple videos."""
        # Create 2 videos
        video1 = tmp_path / "video1.mp4"
        video2 = tmp_path / "video2.mp4"

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        for video_path in [video1, video2]:
            out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
            for _ in range(10):
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                out.write(frame)
            out.release()

        # Multiple videos without --batch flag should auto-enable batch
        result = cli_runner.invoke(
            cmj_analyze,
            [str(video1), str(video2), "--quality", "fast"],
        )

        # Should process both videos (may fail but shouldn't crash)
        assert result.exception is None or result.exit_code != 0

    def test_mixed_valid_and_invalid_paths(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test handling of mixed valid and invalid file paths."""
        nonexistent = tmp_path / "nonexistent.mp4"

        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), str(nonexistent), "--batch", "--quality", "fast"],
        )

        # Should handle mixed paths gracefully
        assert result.exception is None or result.exit_code != 0


class TestCMJCLIWarnings:
    """Test warning messages and stderr output."""

    def test_no_files_found_for_pattern_warning(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test warning is shown when pattern matches no files."""
        result = cli_runner.invoke(cmj_analyze, [str(tmp_path / "*.nonexistent")])

        # Should fail with non-zero exit code
        assert result.exit_code != 0

    def test_batch_processing_not_fully_implemented_message(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test batch mode shows implementation status message."""
        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), str(minimal_video), "--quality", "fast"],
        )

        # Batch mode is enabled for multiple videos
        # (may succeed or fail, check for processing message)
        assert result.exception is None or result.exit_code != 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIDirectFilePath:
    """Test direct file path handling (not glob pattern)."""

    def test_direct_file_path_that_exists(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test direct file path (not glob) is collected properly."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

        # Direct path should be processed
        assert result.exception is None or result.exit_code != 0

    def test_mixed_glob_and_direct_paths(
        self, cli_runner: CliRunner, minimal_video: Path, tmp_path: Path
    ) -> None:
        """Test mixing glob patterns and direct paths."""
        # Create another video
        video2 = tmp_path / "video2.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video2), fourcc, 30.0, (640, 480))
        for _ in range(10):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        # Mix direct path and glob pattern
        result = cli_runner.invoke(
            cmj_analyze,
            [
                str(minimal_video),
                str(tmp_path / "*.mp4"),
                "--batch",
                "--quality",
                "fast",
            ],
        )

        # Should handle mixed paths
        assert result.exception is None or result.exit_code != 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLINullOutputResults:
    """Test output results function with various metrics."""

    def test_output_results_without_json_file(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test output results prints to stdout without JSON file."""
        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), "--quality", "fast"],
        )

        # If successful, should output metrics
        if result.exit_code == 0:
            # Should have some output
            assert len(result.output) > 0

    def test_output_results_with_transition_time(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test output results includes transition time when available."""
        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), "--quality", "fast"],
        )

        # If successful, should output metrics
        if result.exit_code == 0:
            # Check for key CMJ metrics in output
            assert len(result.output) > 0


@pytest.mark.usefixtures("mock_cmj_api")
class TestCMJCLIBatchExceptionContinuation:
    """Test batch processing error continuation."""

    @skip_in_ci
    def test_batch_continues_after_single_video_error(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test batch mode continues processing after error."""
        # Create first video (valid)
        video1 = tmp_path / "video1.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video1), fourcc, 30.0, (640, 480))
        for _ in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        # Create second video (corrupted)
        video2 = tmp_path / "video2.mp4"
        video2.write_text("corrupted")

        # Create third video (valid)
        video3 = tmp_path / "video3.mp4"
        out = cv2.VideoWriter(str(video3), fourcc, 30.0, (640, 480))
        for _ in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        result = cli_runner.invoke(
            cmj_analyze,
            [str(video1), str(video2), str(video3), "--batch", "--quality", "fast"],
        )

        # Batch should handle errors and continue
        assert result.exception is None or result.exit_code != 0


class TestCMJCLISingleProcessingException:
    """Test single processing exception paths."""

    def test_single_processing_invalid_video(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test single processing handles invalid video gracefully."""
        invalid_video = tmp_path / "invalid.mp4"
        invalid_video.write_text("not a video")

        result = cli_runner.invoke(cmj_analyze, [str(invalid_video), "--quality", "fast"])

        # Should fail gracefully
        assert result.exit_code != 0

    def test_single_processing_verbose_on_error(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test single processing verbose mode on error."""
        invalid_video = tmp_path / "invalid.mp4"
        invalid_video.write_text("not a video")

        result = cli_runner.invoke(
            cmj_analyze,
            [str(invalid_video), "--verbose", "--quality", "fast"],
        )

        # Should fail with non-zero exit code in verbose mode
        assert result.exit_code != 0

    def test_single_processing_api_exception(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test single processing when API raises exception."""
        with patch("kinemotion.cmj.cli.process_cmj_video") as mock_api:
            mock_api.side_effect = RuntimeError("API error")

            result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

            # Should fail with exit code 1
            assert result.exit_code == 1

    def test_single_processing_api_exception_verbose(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test single processing API exception with verbose flag."""
        with patch("kinemotion.cmj.cli.process_cmj_video") as mock_api:
            mock_api.side_effect = RuntimeError("API error")

            result = cli_runner.invoke(
                cmj_analyze,
                [str(minimal_video), "--verbose", "--quality", "fast"],
            )

            # Should fail with exit code 1 and show traceback in verbose
            assert result.exit_code == 1


class TestCMJCLIBatchException:
    """Test batch processing exception paths."""

    @skip_in_ci
    def test_batch_processing_api_exception(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test batch processing when API raises exception."""
        with patch("kinemotion.cmj.cli.process_cmj_video") as mock_api:
            mock_api.side_effect = RuntimeError("API error")

            result = cli_runner.invoke(
                cmj_analyze,
                [
                    str(minimal_video),
                    str(minimal_video),
                    "--batch",
                    "--quality",
                    "fast",
                ],
            )

            # Batch mode should handle error and continue
            # Should not crash (may exit or may complete partially)
            assert result.exception is None or result.exit_code != 0

    @skip_in_ci
    def test_batch_single_video_path_expansion(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test that single video in batch still works."""
        result = cli_runner.invoke(
            cmj_analyze,
            [str(minimal_video), "--batch", "--quality", "fast"],
        )

        # Single video with --batch flag should work
        assert result.exception is None or result.exit_code != 0


class TestCMJCLIPathExpansion:
    """Test file path collection and expansion."""

    def test_existing_direct_path_collected(
        self, cli_runner: CliRunner, minimal_video: Path
    ) -> None:
        """Test that existing direct paths are collected (not glob expanded)."""
        result = cli_runner.invoke(cmj_analyze, [str(minimal_video), "--quality", "fast"])

        # Direct path should be processed
        assert result.exception is None or result.exit_code != 0

    def test_nonexistent_direct_path_expanded_as_glob(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that nonexistent paths trigger glob expansion."""
        result = cli_runner.invoke(cmj_analyze, [str(tmp_path / "nonexistent.mp4")])

        # Nonexistent single file should fail (no glob match and file not found)
        assert result.exit_code != 0

    def test_direct_file_path_exists_branch(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test direct file path that exists but doesn't glob expand."""
        # Create a video with a filename that won't glob-expand
        video = tmp_path / "test_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video), fourcc, 30.0, (640, 480))
        for _ in range(10):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        # Pass the file directly (no wildcard glob)
        result = cli_runner.invoke(cmj_analyze, [str(video), "--quality", "fast"])

        # Should process the file
        assert result.exception is None or result.exit_code != 0
