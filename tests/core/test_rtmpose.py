"""Integration tests for RTMPose tracking.

These tests require ONNX Runtime and bundled ONNX models.
Tests are skipped if dependencies are unavailable.
"""

from importlib.util import find_spec
from pathlib import Path

import numpy as np
import pytest

from kinemotion.core.pose import PoseTrackerFactory

pytestmark = [pytest.mark.integration, pytest.mark.core]

# Check if ONNX Runtime is available
onnx_available = find_spec("onnxruntime") is not None

# Check if rtmlib is available (for wrapper tests)
rtmlib_available = find_spec("rtmlib") is not None

# Check if bundled models exist
# These imports are here to avoid ImportError when ONNX models aren't present
if onnx_available:
    from importlib.resources import files

    models_dir = Path(files("kinemotion") / "models")
    det_model_exists = (models_dir / "yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx").exists()
    pose_model_exists = (
        models_dir / "rtmpose-s_simcc-body7_pt-body7-halpe26_700e-256x192-7f134165_20230605.onnx"
    ).exists()
    models_available = det_model_exists and pose_model_exists
else:
    models_available = False


# ===== OptimizedCPUTracker Tests =====


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_rtmpose_factory_creates_cpu_tracker():
    """Test that PoseTrackerFactory can create an RTMPose CPU tracker."""
    tracker = PoseTrackerFactory.create(backend="rtmpose-cpu")
    assert tracker is not None
    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_rtmpose_factory_with_aliases():
    """Test that PoseTrackerFactory accepts RTMPose backend aliases."""
    # Test 'cpu' alias
    tracker1 = PoseTrackerFactory.create(backend="cpu")
    assert tracker1 is not None
    tracker1.close()

    # Test 'rtmpose' alias (should default to CPU)
    tracker2 = PoseTrackerFactory.create(backend="rtmpose")
    assert tracker2 is not None
    tracker2.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_optimized_cpu_tracker_initialization():
    """Test OptimizedCPUTracker initialization with bundled models."""
    from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

    tracker = OptimizedCPUTracker(
        intra_threads=4,
        inter_threads=1,
        verbose=False,
    )
    assert tracker is not None
    assert tracker.det_session is not None
    assert tracker.pose_session is not None
    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_optimized_cpu_tracker_process_frame():
    """Test OptimizedCPUTracker processes a frame and returns landmarks."""
    from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

    tracker = OptimizedCPUTracker(verbose=False)

    # Create a test frame (white background)
    # Note: This is a minimal test - real pose detection requires a person in the frame
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255

    _ = tracker.process_frame(frame)

    # Result may be None if no person is detected (which is expected for blank frame)
    # The important thing is that it doesn't crash
    tracker.close()

    # We just verify the function completes without error
    assert True


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_optimized_cpu_tracker_with_custom_input_size():
    """Test OptimizedCPUTracker with custom input size."""
    from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

    tracker = OptimizedCPUTracker(
        input_size=(256, 192),  # Different input size
        verbose=False,
    )
    assert tracker is not None
    assert tracker.pose_input_size == (192, 256)  # Swapped to (width, height)
    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_optimized_cpu_tracker_thread_configuration():
    """Test OptimizedCPUTracker with custom thread configuration."""
    from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

    tracker = OptimizedCPUTracker(
        intra_threads=2,
        inter_threads=1,
        verbose=False,
    )

    # Verify the tracker was created successfully
    assert tracker is not None
    assert tracker.intra_threads == 2
    assert tracker.inter_threads == 1
    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_optimized_cpu_tracker_empty_frame():
    """Test OptimizedCPUTracker handles empty/invalid frames gracefully."""
    from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

    tracker = OptimizedCPUTracker(verbose=False)

    # Test empty frame
    empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
    result = tracker.process_frame(empty_frame)
    assert result is None

    # Test very small frame
    small_frame = np.ones((10, 10, 3), dtype=np.uint8)
    _ = tracker.process_frame(small_frame)  # Should not crash

    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_optimized_cpu_tracker_verbose_mode():
    """Test OptimizedCPUTracker verbose mode prints information."""
    import sys
    from io import StringIO

    from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

    tracker = OptimizedCPUTracker(verbose=True)

    # Capture output during processing
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
    _ = tracker.process_frame(frame)

    _ = sys.stdout.getvalue()  # Capture to prevent print to actual stdout
    sys.stdout = old_stdout

    # Verbose mode completed without error
    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
def test_onnx_providers_available():
    """Test that ONNX Runtime providers are available."""
    import onnxruntime as ort

    providers = ort.get_available_providers()
    assert len(providers) > 0
    assert "CPUExecutionProvider" in providers


@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_bundled_onnx_models_exist():
    """Test that bundled ONNX models are present."""
    from importlib.resources import files

    models_dir = Path(files("kinemotion") / "models")

    det_model = models_dir / "yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx"
    pose_model = (
        models_dir / "rtmpose-s_simcc-body7_pt-body7-halpe26_700e-256x192-7f134165_20230605.onnx"
    )

    assert det_model.exists(), f"Detector model not found: {det_model}"
    assert pose_model.exists(), f"Pose model not found: {pose_model}"

    # Check file sizes are reasonable (> 10MB)
    assert det_model.stat().st_size > 10_000_000
    assert pose_model.stat().st_size > 10_000_000


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_rtmpose_tracker_interface_compatibility():
    """Test that RTMPose tracker implements the same interface as MediaPipe."""
    tracker = PoseTrackerFactory.create(backend="rtmpose-cpu")

    # Verify the tracker has the required interface
    assert hasattr(tracker, "process_frame")
    assert hasattr(tracker, "close")

    tracker.close()


@pytest.mark.skipif(not onnx_available, reason="ONNX Runtime not installed")
@pytest.mark.skipif(not models_available, reason="Bundled ONNX models not found")
def test_factory_auto_detection_with_rtmpose_available():
    """Test that factory can auto-detect when RTMPose is available."""
    # When RTMPose is available, 'auto' should prefer it over MediaPipe
    # (unless CUDA/CoreML is also available)
    backend = PoseTrackerFactory._detect_best_backend()

    # Should return one of the RTMPose variants or MediaPipe as fallback
    assert backend in [
        "rtmpose-cuda",
        "rtmpose-coreml",
        "rtmpose-cpu",
        "mediapipe",
    ]


# ===== RTMPoseWrapper Tests (require rtmlib) =====


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_rtmpose_wrapper_initialization():
    """Test RTMPoseWrapper initialization."""
    from kinemotion.core.rtmpose_wrapper import RTMPoseWrapper

    wrapper = RTMPoseWrapper(device="cpu")
    assert wrapper is not None
    assert wrapper.device == "cpu"
    assert wrapper.mode == "lightweight"
    wrapper.close()


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_rtmpose_wrapper_with_different_modes():
    """Test RTMPoseWrapper with different performance modes."""
    from kinemotion.core.rtmpose_wrapper import RTMPoseWrapper

    for mode in ["lightweight", "balanced", "performance"]:
        wrapper = RTMPoseWrapper(device="cpu", mode=mode)
        assert wrapper.mode == mode
        wrapper.close()


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_rtmpose_wrapper_process_frame():
    """Test RTMPoseWrapper processes frames."""
    from kinemotion.core.rtmpose_wrapper import RTMPoseWrapper

    wrapper = RTMPoseWrapper(device="cpu")

    # Create test frame
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 100

    # Process frame (may return None if no person detected)
    result = wrapper.process_frame(frame)

    # Result is either None or a dict of landmarks
    assert result is None or isinstance(result, dict)

    wrapper.close()


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_rtmpose_wrapper_empty_frame():
    """Test RTMPoseWrapper handles empty frames."""
    from kinemotion.core.rtmpose_wrapper import RTMPoseWrapper

    wrapper = RTMPoseWrapper(device="cpu")

    # Empty frame
    empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
    result = wrapper.process_frame(empty_frame)
    assert result is None

    wrapper.close()


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_rtmpose_wrapper_landmark_format():
    """Test RTMPoseWrapper returns correct landmark format."""
    from kinemotion.core.rtmpose_wrapper import HALPE_TO_KINEMOTION

    # Verify landmark mapping is complete
    expected_landmarks = {
        "nose",
        "left_shoulder",
        "right_shoulder",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_foot_index",
        "right_foot_index",
        "left_heel",
        "right_heel",
    }

    mapped_landmarks = set(HALPE_TO_KINEMOTION.values())
    assert mapped_landmarks == expected_landmarks


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_rtmpose_wrapper_close_is_noop():
    """Test RTMPoseWrapper.close() is a no-op."""
    from kinemotion.core.rtmpose_wrapper import RTMPoseWrapper

    wrapper = RTMPoseWrapper(device="cpu")
    # close() should not raise any errors
    wrapper.close()
    # Calling close() again should also be safe
    wrapper.close()


@pytest.mark.skipif(not rtmlib_available, reason="rtmlib not installed")
def test_create_rtmpose_wrapper_factory():
    """Test the factory function for creating RTMPoseWrapper."""
    from kinemotion.core.rtmpose_wrapper import create_rtmpose_wrapper

    wrapper = create_rtmpose_wrapper(device="cpu", mode="lightweight")
    assert wrapper is not None
    assert wrapper.device == "cpu"
    assert wrapper.mode == "lightweight"
    wrapper.close()
