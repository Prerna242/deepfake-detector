from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import BASE_DIR, settings
from app.db.mongo import close_mongo_connection
from app.routes import auth, detection


@asynccontextmanager
async def lifespan(app: FastAPI):
    detection_method = settings.DETECTION_METHOD.strip().lower()

    if detection_method == "local":
        from app.ml.model_loader import load_model, set_model_unavailable

        model_path = Path(settings.MODEL_PATH)
        if not model_path.is_absolute():
            model_path = BASE_DIR / model_path

        print("[Startup] Detection mode: local. Loading ML model...")
        try:
            load_model(
                model_path=str(model_path),
                auto_download=settings.MODEL_AUTO_DOWNLOAD,
                download_url=settings.MODEL_DOWNLOAD_URL,
                timeout_seconds=settings.MODEL_DOWNLOAD_TIMEOUT_SECONDS,
                expected_sha256=settings.MODEL_SHA256,
            )
            print("[Startup] ML model ready.")
        except Exception as exc:
            if settings.ALLOW_API_START_WITHOUT_MODEL:
                set_model_unavailable(str(exc))
                print(f"[Startup] WARNING: ML model unavailable. Detection endpoints will return 503. Reason: {exc}")
            else:
                raise
    elif detection_method == "gemini":
        print(f"[Startup] Detection mode: gemini ({settings.GEMINI_MODEL}).")
        if not settings.GEMINI_API_KEY:
            print("[Startup] WARNING: GEMINI_API_KEY is not configured. Detection endpoint will return 503 until configured.")
    else:
        raise ValueError(
            "Unsupported DETECTION_METHOD. Use 'local' or 'gemini' in backend/.env.",
        )

    print("[Startup] Application is ready to accept requests.")

    yield

    print("[Shutdown] Closing MongoDB connection...")
    await close_mongo_connection()
    print("[Shutdown] Goodbye.")


app = FastAPI(
    title="Deepfake Detection API",
    description="Upload an image and find out if it's AI-generated.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(detection.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Deepfake Detection API is running.", "status": "ok"}
