from pathlib import Path
from typing import Callable

from PIL import Image
from torch.utils.data import Dataset


CLASS_TO_LABEL = {"outside": 0, "inside": 1}
IMAGE_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".webp"}


class LaneClassificationDataset(Dataset):
    """Dataset for processed inside/outside lane classification splits."""

    def __init__(self, split_dir: str | Path, transform: Callable | None = None) -> None:
        self.split_dir = Path(split_dir)
        self.transform = transform
        self.samples = self._discover_samples()

    def _discover_samples(self) -> list[tuple[Path, int]]:
        if not self.split_dir.exists():
            raise FileNotFoundError(f"Processed split directory does not exist: {self.split_dir}")
        if not self.split_dir.is_dir():
            raise NotADirectoryError(f"Processed split path is not a directory: {self.split_dir}")

        samples: list[tuple[Path, int]] = []
        missing_classes = [
            class_name
            for class_name in CLASS_TO_LABEL
            if not (self.split_dir / class_name).is_dir()
        ]
        if missing_classes:
            joined = ", ".join(missing_classes)
            raise FileNotFoundError(
                f"Processed split directory {self.split_dir} is missing class folder(s): {joined}"
            )

        empty_classes: list[str] = []
        for class_name, label in CLASS_TO_LABEL.items():
            class_dir = self.split_dir / class_name
            image_paths = sorted(
                path
                for path in class_dir.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            )
            if not image_paths:
                empty_classes.append(class_name)
            samples.extend((path, label) for path in image_paths)

        if empty_classes:
            joined = ", ".join(empty_classes)
            raise ValueError(
                f"Processed split directory {self.split_dir} has empty class folder(s): {joined}"
            )
        if not samples:
            raise ValueError(f"Processed split directory contains no image samples: {self.split_dir}")

        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        image_path, label = self.samples[index]
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            if self.transform is not None:
                image = self.transform(image)
        return image, label
