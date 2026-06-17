import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

import numpy as np
import tensorflow as tf


_model = None
_model_load_error: Optional[str] = None


def set_model_unavailable(reason: str) -> None:
    global _model, _model_load_error
    _model = None
    _model_load_error = reason


def _download_model_file(
    destination: Path,
    url: str,
    timeout_seconds: int,
    expected_sha256: Optional[str] = None,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "deepfake-detector/1.0"},
    )

    hasher = hashlib.sha256()

    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        with tempfile.NamedTemporaryFile(delete=False, dir=str(destination.parent)) as tmp_file:
            temp_path = Path(tmp_file.name)
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                tmp_file.write(chunk)
                hasher.update(chunk)

    if expected_sha256:
        actual = hasher.hexdigest().lower()
        expected = expected_sha256.lower()
        if actual != expected:
            temp_path.unlink(missing_ok=True)
            raise ValueError(
                "Downloaded model checksum mismatch. "
                f"Expected {expected}, got {actual}.",
            )

    temp_path.replace(destination)


def load_model(
    model_path: str,
    auto_download: bool = False,
    download_url: Optional[str] = None,
    timeout_seconds: int = 300,
    expected_sha256: Optional[str] = None,
) -> None:
    global _model, _model_load_error

    model_file = Path(model_path)

    if not model_file.exists() and auto_download:
        if not download_url:
            raise ValueError(
                "MODEL_AUTO_DOWNLOAD is enabled, but MODEL_DOWNLOAD_URL is not set.",
            )
        print(f"[ML] Model not found at {model_file}. Downloading pretrained model...")
        _download_model_file(
            destination=model_file,
            url=download_url,
            timeout_seconds=timeout_seconds,
            expected_sha256=expected_sha256,
        )
        print(f"[ML] Model downloaded to: {model_file}")

    if not os.path.exists(model_file):
        raise FileNotFoundError(
            f"Model file not found at: {model_file}\n"
            "Provide a pretrained model file, train one locally, or enable MODEL_AUTO_DOWNLOAD with MODEL_DOWNLOAD_URL.",
        )

    print(f"[ML] Loading model from: {model_file}")
    _model = tf.keras.models.load_model(model_file)
    _model_load_error = None
    print(f"[ML] Model loaded successfully. Input shape: {_model.input_shape}")


def get_model() -> tf.keras.Model:
    if _model is None:
        if _model_load_error:
            raise RuntimeError(f"Model is unavailable: {_model_load_error}")
        raise RuntimeError("Model has not been loaded. Call load_model() during app startup.")
    return _model


def predict(preprocessed_image: np.ndarray) -> dict:
    model = get_model()
    raw_score = float(model.predict(preprocessed_image, verbose=0)[0][0])

    if raw_score > 0.5:
        label = "REAL"
        confidence = round(raw_score * 100, 2)
    else:
        label = "FAKE"
        confidence = round((1.0 - raw_score) * 100, 2)

    return {
        "label": label,
        "confidence": confidence,
        "raw_score": raw_score,
    }
