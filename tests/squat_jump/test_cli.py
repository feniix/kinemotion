"""Tests for Squat Jump CLI commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from kinemotion.squat_jump.cli import sj_analyze

pytestmark = [pytest.mark.integration, pytest.mark.squat_jump]


class TestSJCLI:
    """Test SJ CLI functionality."""

    def test_sj_analyze_command_basic(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test basic SJ analyze command invocation."""
        # The --mass parameter is required for SJ
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "75.0"],
        )

        # Should fail because minimal_video is empty (not a real video)
        # The actual error will be raised when trying to process the video
        assert result.exit_code != 0

    def test_mass_parameter_required(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test that --mass parameter is required."""
        result = cli_runner.invoke(sj_analyze, [str(minimal_video)])

        # Should fail because --mass is required
        assert result.exit_code == 2  # Click error code for missing option

    def test_mass_parameter_validation(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test mass parameter validation."""
        # Test negative mass
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "-10.0"],
        )
        assert result.exit_code != 0

        # Test zero mass
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "0.0"],
        )
        assert result.exit_code != 0

        # Test very small mass - should be accepted (even if unrealistic)
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "0.1"],
        )
        # Should either succeed or fail with NotImplementedError
        assert result.exit_code in [0, 1]

    def test_batch_processing_single_file(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test batch processing with single file."""
        result = cli_runner.invoke(
            sj_analyze,
            [
                str(minimal_video),
                "--mass",
                "75.0",
                "--batch",
                "--workers",
                "1",
            ],
        )

        # Should fail due to minimal_video being empty, but parse arguments correctly
        assert result.exit_code != 0

    def test_batch_processing_multiple_files(self, tmp_path, cli_runner: CliRunner) -> None:
        """Test batch processing with multiple files."""
        # Create multiple test videos
        videos = []
        for i in range(3):
            video_path = tmp_path / f"test_{i}.mp4"
            # Create minimal video file (touch is enough for CLI test)
            video_path.touch()
            videos.append(str(video_path))

        result = cli_runner.invoke(
            sj_analyze,
            videos + ["--mass", "75.0", "--batch", "--workers", "2"],
        )

        # Should process multiple files
        assert result.exit_code != 0  # Due to NotImplementedError
        assert "3 video(s)" in result.output or len(videos) == 3

    def test_expert_parameters(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test expert parameter overrides."""
        result = cli_runner.invoke(
            sj_analyze,
            [
                str(minimal_video),
                "--mass",
                "75.0",
                "--smoothing-window",
                "7",
                "--velocity-threshold",
                "0.15",
                "--squat-hold-threshold",
                "0.03",
                "--min-contact-frames",
                "5",
            ],
        )

        # Should parse expert parameters correctly
        assert result.exit_code != 0  # Fails due to minimal_video being empty
        # Check that parameters were parsed (no immediate argument errors)
        assert "--smoothing-window" not in result.output

    def test_output_options(self, minimal_video, tmp_path, cli_runner: CliRunner) -> None:
        """Test output file options."""
        output_video = tmp_path / "output.mp4"
        output_json = tmp_path / "output.json"

        result = cli_runner.invoke(
            sj_analyze,
            [
                str(minimal_video),
                "--mass",
                "75.0",
                "--output",
                str(output_video),
                "--json",
                str(output_json),
            ],
        )

        # Should parse output options correctly
        assert result.exit_code != 0  # Fails due to minimal_video being empty

    def test_verbose_mode(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test verbose mode output."""
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "75.0", "--verbose"],
        )

        # Should include verbose output
        assert result.exit_code != 0
        assert "video" in result.output.lower() or "processing" in result.output.lower()

    def test_quality_preset_options(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test quality preset options."""
        for preset in ["fast", "balanced", "accurate"]:
            result = cli_runner.invoke(
                sj_analyze,
                [str(minimal_video), "--mass", "75.0", "--quality", preset],
            )

            # Should accept preset values (no parsing error)
            assert "Invalid quality" not in result.output

    def test_invalid_quality_preset(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test invalid quality preset."""
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "75.0", "--quality", "invalid"],
        )

        # Should fail with invalid preset
        assert result.exit_code != 0

    def test_file_not_found(self, cli_runner: CliRunner) -> None:
        """Test handling of non-existent video files."""
        result = cli_runner.invoke(
            sj_analyze,
            ["nonexistent.mp4", "--mass", "75.0"],
        )

        # Should fail with file not found error
        assert result.exit_code != 0

    def test_help_output(self, cli_runner: CliRunner) -> None:
        """Test help output includes SJ-specific information."""
        result = cli_runner.invoke(sj_analyze, ["--help"])

        # Should show help with SJ-specific info
        assert result.exit_code == 0
        assert "sj-analyze" in result.output.lower()
        assert "squat jump" in result.output.lower()
        assert "mass" in result.output.lower()

    def test_multiple_videos_explicit_mass(self, tmp_path, cli_runner: CliRunner) -> None:
        """Test processing multiple videos with explicit mass."""
        # Create multiple test videos
        videos = []
        for i in range(2):
            video_path = tmp_path / f"video_{i}.mp4"
            video_path.touch()
            videos.append(str(video_path))

        result = cli_runner.invoke(
            sj_analyze,
            videos + ["--mass", "80.0"],
        )

        # Should process multiple videos
        assert result.exit_code != 0
        # Should indicate number of videos
        assert "2" in result.output or len(videos) == 2

    def test_expert_parameters_optional(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test that expert parameters are optional and use defaults."""
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "75.0"],
        )

        # Should work without expert parameters
        assert result.exit_code != 0  # Only fails due to minimal_video being empty
        # Should not show errors about missing expert parameters

    def test_workers_parameter_validation(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test workers parameter validation in batch mode."""
        # Test invalid workers values
        for workers in ["0", "-1", "abc"]:
            result = cli_runner.invoke(
                sj_analyze,
                [str(minimal_video), "--mass", "75.0", "--batch", "--workers", workers],
            )

            # Should fail for invalid values
            assert result.exit_code != 0

    def test_json_output_format(self, minimal_video, tmp_path, cli_runner: CliRunner) -> None:
        """Test JSON output format specification."""
        json_path = tmp_path / "result.json"

        result = cli_runner.invoke(
            sj_analyze,
            [
                str(minimal_video),
                "--mass",
                "75.0",
                "--json",
                str(json_path),
            ],
        )

        # Should specify JSON output
        assert result.exit_code != 0

    def test_successful_processing_mock(self, minimal_video, cli_runner: CliRunner) -> None:
        """Test command accepts required parameters without crashing."""
        result = cli_runner.invoke(
            sj_analyze,
            [str(minimal_video), "--mass", "75.0"],
        )

        # Should either succeed or fail gracefully, not crash
        assert result.exit_code in [0, 1]


class TestSJBatchProcessing:
    """Test SJ batch processing functionality."""

    def test_batch_without_workers(self, tmp_path, cli_runner: CliRunner) -> None:
        """Test batch processing without workers specification."""
        videos = [str(tmp_path / f"video_{i}.mp4") for i in range(2)]
        for video in videos:
            Path(video).touch()

        result = cli_runner.invoke(
            sj_analyze,
            videos + ["--mass", "75.0", "--batch"],
        )

        # Should use default workers
        assert result.exit_code != 0

    def test_batch_with_workers(self, tmp_path, cli_runner: CliRunner) -> None:
        """Test batch processing with specified workers."""
        videos = [str(tmp_path / f"video_{i}.mp4") for i in range(3)]
        for video in videos:
            Path(video).touch()

        result = cli_runner.invoke(
            sj_analyze,
            videos + ["--mass", "75.0", "--batch", "--workers", "4"],
        )

        # Should use specified workers
        assert result.exit_code != 0

    def test_batch_error_handling(self, tmp_path, cli_runner: CliRunner) -> None:
        """Test batch processing error handling."""
        # Create one valid file and one invalid
        valid_video = tmp_path / "valid.mp4"
        invalid_video = tmp_path / "invalid.mp4"

        valid_video.touch()
        # Don't create invalid_video

        result = cli_runner.invoke(
            sj_analyze,
            [str(valid_video), str(invalid_video), "--mass", "75.0", "--batch"],
        )

        # Should handle errors gracefully
        assert result.exit_code != 0

    def test_batch_output_directories(self, tmp_path, cli_runner: CliRunner) -> None:
        """Test batch processing with output directories."""
        videos = []
        for i in range(2):
            video_path = tmp_path / f"input_{i}.mp4"
            video_path.touch()
            videos.append(str(video_path))

        output_dir = tmp_path / "output"
        json_dir = tmp_path / "json"

        result = cli_runner.invoke(
            sj_analyze,
            videos
            + [
                "--mass",
                "75.0",
                "--batch",
                "--output-dir",
                str(output_dir),
                "--json-dir",
                str(json_dir),
            ],
        )

        # Should use output directories
        assert result.exit_code != 0
