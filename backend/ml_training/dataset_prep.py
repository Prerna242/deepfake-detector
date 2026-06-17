import os
import random
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

RAW_REAL_DIR = PROJECT_ROOT / "dataset" / "raw" / "real"
RAW_FAKE_DIR = PROJECT_ROOT / "dataset" / "raw" / "fake"
OUTPUT_DIR = PROJECT_ROOT / "dataset"

TRAIN_RATIO = 0.75
VAL_RATIO = 0.15
TEST_RATIO = 0.10


def split_and_copy(source_dir: Path, label: str, output_dir: Path) -> None:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    all_images = [
        file_name
        for file_name in os.listdir(source_dir)
        if file_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    random.shuffle(all_images)

    total = len(all_images)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    splits = {
        "train": all_images[:train_end],
        "validation": all_images[train_end:val_end],
        "test": all_images[val_end:],
    }

    for split_name, files in splits.items():
        destination = output_dir / split_name / label
        destination.mkdir(parents=True, exist_ok=True)

        for filename in files:
            shutil.copy(
                source_dir / filename,
                destination / filename,
            )

        print(f"Copied {len(files)} images to {destination}")


if __name__ == "__main__":
    if abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) > 1e-9:
        raise ValueError("TRAIN_RATIO + VAL_RATIO + TEST_RATIO must equal 1.0")

    random.seed(42)
    split_and_copy(RAW_REAL_DIR, "real", OUTPUT_DIR)
    split_and_copy(RAW_FAKE_DIR, "fake", OUTPUT_DIR)
    print("Dataset preparation complete.")
