from pathlib import Path
from typing import Callable

import torch
from torch import nn

from lane_classification.dataset import CLASS_TO_LABEL
from lane_classification.model import create_resnet18_binary_model


DEFAULT_CLASS_NAMES = [
    class_name
    for class_name, _ in sorted(CLASS_TO_LABEL.items(), key=lambda item: item[1])
]


def save_checkpoint(
    model: nn.Module,
    checkpoint_path: str | Path,
    class_names: list[str] | None = None,
    metadata: dict | None = None,
) -> Path:
    path = Path(checkpoint_path)
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    names = list(class_names or DEFAULT_CLASS_NAMES)
    if len(names) != 2:
        raise ValueError("class_names must contain exactly two labels")
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "class_names": names,
            "metadata": metadata or {},
        },
        path,
    )
    return path


def load_checkpoint(
    checkpoint_path: str | Path,
    device: str | torch.device = "cpu",
    model_factory: Callable[[], nn.Module] = create_resnet18_binary_model,
) -> tuple[nn.Module, list[str], dict]:
    path = Path(checkpoint_path)
    if not path.is_file():
        raise FileNotFoundError(f"Checkpoint does not exist: {path}")

    checkpoint = torch.load(path, map_location=torch.device(device), weights_only=False)
    if not isinstance(checkpoint, dict):
        raise ValueError("Checkpoint must be a dictionary")
    if "model_state_dict" not in checkpoint:
        raise ValueError("Checkpoint is missing model_state_dict")
    class_names = checkpoint.get("class_names")
    if not isinstance(class_names, list) or len(class_names) != 2:
        raise ValueError("Checkpoint is missing two class_names")

    model = model_factory()
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, list(class_names), checkpoint
