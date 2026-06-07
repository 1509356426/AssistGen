from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable, Sequence

import torch
from torch import nn
from torch.utils.data import DataLoader

from lane_classification.checkpoint import load_checkpoint
from lane_classification.dataset import LaneClassificationDataset
from lane_classification.metrics import compute_binary_metrics
from lane_classification.model import create_resnet18_binary_model
from lane_classification.transforms import get_eval_transform
from lane_classification.train import _positive_int


def evaluate_checkpoint(
    checkpoint_path: str | Path,
    data_dir: str | Path,
    batch_size: int = 8,
    device: str = "cpu",
    image_size: int = 224,
    metrics_path: str | Path | None = None,
    model_factory: Callable[[], nn.Module] = create_resnet18_binary_model,
) -> dict:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if image_size <= 0:
        raise ValueError("image_size must be positive")

    model, class_names, _ = load_checkpoint(checkpoint_path, device=device, model_factory=model_factory)
    dataset = LaneClassificationDataset(data_dir, transform=get_eval_transform(image_size))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    true_labels: list[int] = []
    predicted_labels: list[int] = []

    model.eval()
    with torch.no_grad():
        for images, labels in loader:
            logits = model(images.to(device))
            predicted_labels.extend(logits.argmax(dim=1).cpu().tolist())
            true_labels.extend(labels.tolist())

    metrics = compute_binary_metrics(true_labels, predicted_labels)
    metrics["class_names"] = class_names
    metrics["num_samples"] = len(true_labels)
    if metrics_path is not None:
        path = Path(metrics_path)
        if path.parent:
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    return metrics


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a lane classifier checkpoint.")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--batch-size", type=_positive_int, default=8)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--image-size", type=_positive_int, default=224)
    parser.add_argument("--metrics-json", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.checkpoint.is_file():
        parser.error(f"--checkpoint must be an existing file: {args.checkpoint}")
    if not args.data_dir.is_dir():
        parser.error(f"--data-dir must be an existing directory: {args.data_dir}")

    metrics = evaluate_checkpoint(
        checkpoint_path=args.checkpoint,
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        device=args.device,
        image_size=args.image_size,
        metrics_path=args.metrics_json,
    )
    print(json.dumps(metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
