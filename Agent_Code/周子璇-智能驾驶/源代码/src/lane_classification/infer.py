from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable, Sequence

import torch
from PIL import Image
from torch import nn

from lane_classification.checkpoint import load_checkpoint
from lane_classification.model import create_resnet18_binary_model
from lane_classification.transforms import get_eval_transform
from lane_classification.train import _positive_int


def predict_image(
    checkpoint_path: str | Path,
    image_path: str | Path,
    device: str = "cpu",
    image_size: int = 224,
    model_factory: Callable[[], nn.Module] = create_resnet18_binary_model,
) -> dict:
    if image_size <= 0:
        raise ValueError("image_size must be positive")
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image does not exist: {path}")

    model, class_names, _ = load_checkpoint(checkpoint_path, device=device, model_factory=model_factory)
    transform = get_eval_transform(image_size)
    with Image.open(path) as image:
        tensor = transform(image.convert("RGB")).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        probabilities = torch.softmax(model(tensor), dim=1)[0].cpu()
    index = int(probabilities.argmax().item())
    return {
        "label": class_names[index],
        "confidence": float(probabilities[index].item()),
        "probabilities": {
            class_names[class_index]: float(probability)
            for class_index, probability in enumerate(probabilities.tolist())
        },
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predict inside/outside for one image.")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--image-size", type=_positive_int, default=224)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.checkpoint.is_file():
        parser.error(f"--checkpoint must be an existing file: {args.checkpoint}")
    if not args.image.is_file():
        parser.error(f"--image must be an existing file: {args.image}")

    prediction = predict_image(
        checkpoint_path=args.checkpoint,
        image_path=args.image,
        device=args.device,
        image_size=args.image_size,
    )
    print(json.dumps(prediction, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
