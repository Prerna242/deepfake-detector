import asyncio
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiofiles

from app.config import BASE_DIR, settings
from app.db.mongo import get_database
from app.services.gemini_detection_service import predict_with_gemini


def _resolve_mime_type(file_ext: str, content_type: str | None) -> str:
    if content_type in {"image/jpeg", "image/png", "image/webp"}:
        return content_type
    if file_ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if file_ext == ".png":
        return "image/png"
    if file_ext == ".webp":
        return "image/webp"
    return "image/jpeg"


def _resolve_path_from_setting(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


async def _write_bytes_to_path(path: Path, file_bytes: bytes) -> None:
    async with aiofiles.open(path, "wb") as file_handle:
        await file_handle.write(file_bytes)


async def run_detection(
    file_bytes: bytes,
    original_filename: str,
    user_id: str,
    content_type: str | None = None,
) -> dict:
    file_ext = os.path.splitext(original_filename)[1].lower()
    if not file_ext:
        file_ext = ".jpg"

    unique_id = str(uuid.uuid4())
    save_name = f"{unique_id}{file_ext}"

    upload_dir = _resolve_path_from_setting(settings.UPLOAD_DIR)
    save_path = upload_dir / save_name

    paths_to_write = [save_path]
    if settings.PARALLEL_BACKEND_SAVE_ENABLED:
        backend_copy_dir = _resolve_path_from_setting(settings.PARALLEL_BACKEND_SAVE_DIR)
        backend_copy_path = backend_copy_dir / save_name
        if backend_copy_path != save_path:
            paths_to_write.append(backend_copy_path)

    for path in paths_to_write:
        path.parent.mkdir(parents=True, exist_ok=True)

    await asyncio.gather(*(_write_bytes_to_path(path, file_bytes) for path in paths_to_write))

    detection_method = settings.DETECTION_METHOD.strip().lower()
    if detection_method == "gemini":
        prediction = await predict_with_gemini(
            file_bytes=file_bytes,
            mime_type=_resolve_mime_type(file_ext=file_ext, content_type=content_type),
        )
    elif detection_method == "local":
        from app.ml.model_loader import predict
        from app.ml.preprocessor import full_preprocess_pipeline

        processed_image = full_preprocess_pipeline(file_bytes)
        prediction = predict(processed_image)
    else:
        raise RuntimeError(
            "Unsupported DETECTION_METHOD. Use 'local' or 'gemini' in backend/.env."
        )

    scan_id = str(uuid.uuid4())
    scanned_at = datetime.now(timezone.utc)

    scan_doc = {
        "scan_id": scan_id,
        "user_id": user_id,
        "filename": original_filename,
        "saved_as": save_name,
        "label": prediction["label"],
        "confidence": prediction["confidence"],
        "raw_score": prediction["raw_score"],
        "scanned_at": scanned_at,
    }

    db = get_database()
    await db["scans"].insert_one(scan_doc)

    return {
        "scan_id": scan_id,
        "label": prediction["label"],
        "confidence": prediction["confidence"],
        "raw_score": prediction["raw_score"],
        "filename": original_filename,
        "scanned_at": scanned_at,
    }
