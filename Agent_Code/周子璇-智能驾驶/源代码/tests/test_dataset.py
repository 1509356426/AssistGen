from pathlib import Path

import pytest
import torch
from PIL import Image

from lane_classification.dataset import CLASS_TO_LABEL, LaneClassificationDataset
from lane_classification.transforms import get_eval_transform, get_train_transform


def _write_image(path: Path, color: tuple[int, int, int] = (32, 64, 96)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (12, 8), color=color).save(path)


def _write_split(root: Path) -> Path:
    split_dir = root / "train"
    _write_image(split_dir / "outside" / "outside_1.png")
    _write_image(split_dir / "inside" / "inside_1.jpg", color=(96, 64, 32))
    return split_dir


def test_dataset_loads_processed_split_with_fixed_labels(tmp_path: Path) -> None:
    split_dir = _write_split(tmp_path)

    dataset = LaneClassificationDataset(split_dir, transform=get_eval_transform((16, 20)))

    assert len(dataset) == 2
    assert [label for _, label in dataset.samples] == [
        CLASS_TO_LABEL["outside"],
        CLASS_TO_LABEL["inside"],
    ]

    image, label = dataset[0]
    assert isinstance(image, torch.Tensor)
    assert image.shape == (3, 16, 20)
    assert image.dtype == torch.float32
    assert isinstance(label, int)
    assert label == 0


def test_dataset_reports_missing_split_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Processed split directory does not exist"):
        LaneClassificationDataset(tmp_path / "missing")


def test_dataset_reports_missing_class_folder(tmp_path: Path) -> None:
    split_dir = tmp_path / "train"
    _write_image(split_dir / "inside" / "inside.png")

    with pytest.raises(FileNotFoundError, match="missing class folder"):
        LaneClassificationDataset(split_dir)


def test_dataset_reports_empty_class_folder(tmp_path: Path) -> None:
    split_dir = tmp_path / "train"
    (split_dir / "outside").mkdir(parents=True)
    _write_image(split_dir / "inside" / "inside.png")

    with pytest.raises(ValueError, match="empty class folder"):
        LaneClassificationDataset(split_dir)


def test_train_and_eval_transforms_return_expected_tensor_shape() -> None:
    image = Image.new("RGB", (10, 12), color=(128, 128, 128))

    train_tensor = get_train_transform(24)(image)
    eval_transform = get_eval_transform((18, 22))
    eval_tensor_1 = eval_transform(image)
    eval_tensor_2 = eval_transform(image)

    assert train_tensor.shape == (3, 24, 24)
    assert train_tensor.dtype == torch.float32
    assert eval_tensor_1.shape == (3, 18, 22)
    assert torch.equal(eval_tensor_1, eval_tensor_2)
