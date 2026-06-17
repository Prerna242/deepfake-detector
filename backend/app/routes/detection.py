from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.middleware.auth_middleware import get_current_user
from app.models.scan import ScanHistoryResponse, ScanResult
from app.services.detection_service import run_detection
from app.services.history_service import get_user_history


router = APIRouter(prefix="/api", tags=["Detection"])

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/detect", response_model=ScanResult)
async def detect_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file type: {file.content_type}. "
                "Only JPG, PNG, and WEBP are allowed."
            ),
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 5MB.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file received.",
        )

    try:
        filename = file.filename or "uploaded_image"
        return await run_detection(
            file_bytes=file_bytes,
            original_filename=filename,
            user_id=current_user["id"],
            content_type=file.content_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during detection. Please try again.",
        ) from None


@router.get("/history", response_model=ScanHistoryResponse)
async def get_history(current_user: dict = Depends(get_current_user)):
    return await get_user_history(user_id=current_user["id"])
