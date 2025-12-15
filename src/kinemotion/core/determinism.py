"""Determinism utilities for reproducible analysis.

Provides functions to set random seeds for NumPy, Python's random module,
and TensorFlow (used by MediaPipe) to ensure deterministic behavior.
"""

import hashlib
import os
import random
from pathlib import Path

import numpy as np


def get_video_hash_seed(video_path: str) -> int:
    """Generate deterministic seed from video file path.

    Uses video filename (not contents) to generate a consistent seed
    for the same video across multiple runs.

    Args:
        video_path: Path to video file

    Returns:
        Integer seed value derived from filename
    """
    # Use filename only (not full path) for consistency
    filename = Path(video_path).name
    # Hash filename to get deterministic seed
    hash_value = hashlib.md5(filename.encode()).hexdigest()
    # Convert first 8 hex chars to integer
    return int(hash_value[:8], 16)


def set_deterministic_mode(seed: int | None = None, video_path: str | None = None) -> None:
    """Set random seeds for reproducible analysis.

    Sets seeds for:
    - Python's random module
    - NumPy random number generator
    - TensorFlow (via environment variable for TFLite)

    Args:
        seed: Random seed value. If None and video_path provided,
              generates seed from video filename.
        video_path: Optional video path to generate deterministic seed

    Note:
        This should be called before any MediaPipe or analysis operations
        to ensure deterministic pose detection and metric calculation.
    """
    # Generate seed from video if not provided
    if seed is None and video_path is not None:
        seed = get_video_hash_seed(video_path)
    elif seed is None:
        seed = 42  # Default

    # Python random
    random.seed(seed)

    # NumPy random
    np.random.seed(seed)

    # TensorFlow/TFLite (used by MediaPipe)
    # Set via environment variable before TF is initialized
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["TF_DETERMINISTIC_OPS"] = "1"

    # Try to set TensorFlow seed if available
    try:
        import tensorflow as tf

        tf.random.set_seed(seed)

        # Disable GPU non-determinism if CUDA is available
        try:
            tf.config.experimental.enable_op_determinism()
        except AttributeError:
            # Older TensorFlow versions don't have this
            pass
    except ImportError:
        # TensorFlow not directly available (only via MediaPipe's bundled version)
        pass
