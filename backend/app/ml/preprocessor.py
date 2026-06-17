import io

import cv2
import numpy as np
from PIL import Image


IMG_SIZE = 224


def load_and_validate_image(file_bytes: bytes) -> np.ndarray:
    try:
        pil_image = Image.open(io.BytesIO(file_bytes))
        pil_image = pil_image.convert("RGB")

        img_array = np.array(pil_image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        return img_bgr
    except Exception as exc:
        raise ValueError(
            "Invalid image file. Please upload a JPG, PNG, or WEBP image.",
        ) from exc


def detect_and_crop_face(img_bgr: np.ndarray) -> np.ndarray:
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
    )

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60),
    )

    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda face: face[2] * face[3])

        margin = int(0.15 * max(w, h))
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(img_bgr.shape[1], x + w + margin)
        y2 = min(img_bgr.shape[0], y + h + margin)

        return img_bgr[y1:y2, x1:x2]

    return img_bgr


def preprocess_for_model(img_bgr: np.ndarray) -> np.ndarray:
    img_resized = cv2.resize(img_bgr, (IMG_SIZE, IMG_SIZE))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_normalized = img_rgb.astype(np.float32) / 255.0
    img_batch = np.expand_dims(img_normalized, axis=0)

    return img_batch


def full_preprocess_pipeline(file_bytes: bytes) -> np.ndarray:
    img_bgr = load_and_validate_image(file_bytes)
    img_face = detect_and_crop_face(img_bgr)
    img_ready = preprocess_for_model(img_face)
    return img_ready
