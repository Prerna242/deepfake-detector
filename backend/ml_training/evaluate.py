import os
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

MODEL_PATH = BACKEND_DIR / "saved_model" / "efficientnet_deepfake.h5"
TEST_DIR = PROJECT_ROOT / "dataset" / "test"
IMG_SIZE = 224
BATCH_SIZE = 32


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found at {MODEL_PATH}. Run backend/ml_training/train.py first.",
    )

model = tf.keras.models.load_model(str(MODEL_PATH))

test_datagen = ImageDataGenerator(rescale=1.0 / 255.0)
test_gen = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False,
)

loss, accuracy = model.evaluate(test_gen)
print(f"\nTest Loss:     {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
print("\nClass indices:", test_gen.class_indices)
