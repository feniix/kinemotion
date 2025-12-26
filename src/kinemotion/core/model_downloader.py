"""Model file loader for MediaPipe Tasks API.

The Tasks API requires model files (.task). This module handles:
1. Using bundled model files (included in package)
2. Fallback to downloading and caching if bundled file not found
"""

from __future__ import annotations

import hashlib
import urllib.request
from importlib.resources import as_file, files
from pathlib import Path

from platformdirs import user_cache_dir

# Model URLs from Google's MediaPipe model storage
MODEL_URLS: dict[str, str] = {
    "lite": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
    "full": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task",
    "heavy": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task",
}

# Expected SHA256 hashes for model verification (placeholder - should be filled in)
MODEL_HASHES: dict[str, str] = {
    "lite": "",
    "full": "",
    "heavy": "",
}


def _get_bundled_model_path(model_type: str) -> Path | None:
    """Get the path to a bundled model file in the package.

    For zip installs, copies the model to the cache directory first.

    Args:
        model_type: Model variant ("lite", "full", or "heavy")

    Returns:
        Path to model file, or None if not found
    """
    import shutil

    try:
        model_filename = f"pose_landmarker_{model_type}.task"
        package = files("kinemotion.models") / model_filename
        if package.is_file():
            # For editable installs, files are directly accessible
            # Check if we can use it directly (it's a real file path)
            try:
                # Try to get the path without extraction
                direct_path = Path(str(package))
                if direct_path.is_file():
                    return direct_path
            except (TypeError, ValueError):
                pass

            # For zip installs, extract to cache
            cache_dir = get_model_cache_dir()
            cached_model = cache_dir / model_filename

            # Only copy if not already cached
            if not cached_model.exists():
                with as_file(package) as extracted:
                    shutil.copy(extracted, cached_model)

            return cached_model
    except Exception:
        # Package data not available
        pass
    return None


def get_model_cache_dir() -> Path:
    """Get the cache directory for model files.

    Returns:
        Path to the cache directory (platform-specific)
    """
    cache_dir = Path(user_cache_dir("kinemotion", appauthor=False))
    models_dir = cache_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def get_model_path(model_type: str = "heavy") -> Path:
    """Get the path to a model file.

    Priority order:
    1. Bundled model in package (no download needed)
    2. Cached model from previous download
    3. Download from Google's storage

    Args:
        model_type: Model variant ("lite", "full", or "heavy")

    Returns:
        Path to the model file

    Raises:
        ValueError: If model_type is not recognized
    """
    if model_type not in MODEL_URLS:
        valid_types = ", ".join(MODEL_URLS.keys())
        raise ValueError(f"Unknown model type: {model_type}. Choose from: {valid_types}")

    # 1. Try bundled model first (fastest - no download)
    bundled_path = _get_bundled_model_path(model_type)
    if bundled_path is not None:
        return bundled_path

    # 2. Check cache
    cache_dir = get_model_cache_dir()
    model_filename = f"pose_landmarker_{model_type}.task"
    model_path = cache_dir / model_filename

    if model_path.exists():
        return model_path

    # 3. Download the model
    url = MODEL_URLS[model_type]
    _download_file(url, model_path)

    return model_path


def _download_file(url: str, destination: Path) -> None:
    """Download a file from URL to destination.

    Args:
        url: Source URL
        destination: Destination path

    Raises:
        urllib.error.URLError: If download fails
    """
    temp_path = destination.with_suffix(".tmp")

    try:
        with urllib.request.urlopen(url) as response:
            with temp_path.open("wb") as f:
                while chunk := response.read(8192):
                    f.write(chunk)
        temp_path.replace(destination)
    except Exception:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise


def verify_model_hash(model_path: Path, expected_hash: str) -> bool:
    """Verify a model file's SHA256 hash.

    Args:
        model_path: Path to the model file
        expected_hash: Expected SHA256 hash

    Returns:
        True if hash matches, False otherwise
    """
    sha256_hash = hashlib.sha256()

    with model_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest() == expected_hash


__all__ = ["get_model_path", "get_model_cache_dir", "verify_model_hash", "MODEL_URLS"]
