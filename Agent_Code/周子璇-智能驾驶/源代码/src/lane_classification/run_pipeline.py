from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence

from torch import nn

from lane_classification.evaluate import evaluate_checkpoint
from lane_classification.infer import predict_image
from lane_classification.model import create_resnet18_binary_model
from lane_classification.prepare_tusimple import prepare_tusimple_dataset
from lane_classification.synthetic import generate_synthetic_tusimple
from lane_classification.train import TrainingConfig, _positive_float, _positive_int, train_model


@dataclass(frozen=True)
class PipelineConfig:
    workspace: Path
    smoke: bool = False
    epochs: int = 1
    batch_size: int = 2
    lr: float = 1e-3
    image_size: int = 32
    device: str = "cpu"
    seed: int = 0
    train_count: int = 4
    val_count: int = 2
    skip_onnx: bool = False


def run_pipeline(
    config: PipelineConfig,
    model_factory: Callable[[], nn.Module] = create_resnet18_binary_model,
) -> dict:
    if not config.smoke:
        raise ValueError("run_pipeline currently requires smoke=True")
    _validate_config(config)

    workspace = config.workspace
    raw_root = workspace / "raw_synthetic"
    processed_root = workspace / "processed"
    checkpoint_path = workspace / "checkpoints" / "lane.pt"
    metrics_path = workspace / "metrics.json"
    onnx_path = workspace / "exports" / "lane.onnx"
    log_dir = workspace / "runs"
    summary_path = workspace / "summary.json"

    print("[1/6] Generating synthetic TuSimple data")
    train_annotations = generate_synthetic_tusimple(raw_root, split="train", count=config.train_count)
    val_annotations = generate_synthetic_tusimple(raw_root, split="val", count=config.val_count)

    print("[2/6] Preparing inside/outside ROI samples")
    processed_counts = _prepare_smoke_dataset(
        raw_root=raw_root,
        processed_root=processed_root,
        train_annotations=train_annotations,
        val_annotations=val_annotations,
    )

    print("[3/6] Training classifier")
    train_result = train_model(
        TrainingConfig(
            train_dir=processed_root / "train",
            checkpoint_path=checkpoint_path,
            val_dir=processed_root / "val",
            log_dir=log_dir,
            epochs=config.epochs,
            batch_size=config.batch_size,
            lr=config.lr,
            device=config.device,
            image_size=config.image_size,
            seed=config.seed,
        ),
        model_factory=model_factory,
    )

    print("[4/6] Evaluating checkpoint")
    metrics = evaluate_checkpoint(
        checkpoint_path=checkpoint_path,
        data_dir=processed_root / "val",
        batch_size=config.batch_size,
        device=config.device,
        image_size=config.image_size,
        metrics_path=metrics_path,
        model_factory=model_factory,
    )

    print("[5/6] Running PyTorch inference")
    image_path = _pick_validation_image(processed_root / "val")
    pytorch_prediction = predict_image(
        checkpoint_path=checkpoint_path,
        image_path=image_path,
        device=config.device,
        image_size=config.image_size,
        model_factory=model_factory,
    )

    onnx_prediction = None
    if not config.skip_onnx:
        print("[6/6] Exporting ONNX and running ONNX Runtime inference")
        from lane_classification.export_onnx import export_checkpoint_to_onnx
        from lane_classification.infer_onnx import predict_onnx_image

        exported_onnx_path = export_checkpoint_to_onnx(
            checkpoint_path=checkpoint_path,
            output_path=onnx_path,
            image_size=config.image_size,
            device=config.device,
            model_factory=model_factory,
        )
        onnx_prediction = predict_onnx_image(
            model_path=exported_onnx_path,
            image_path=image_path,
            image_size=config.image_size,
        )
    else:
        print("[6/6] Skipping ONNX export/inference")

    summary = {
        "config": _jsonable_config(config),
        "workspace": str(workspace),
        "raw_root": str(raw_root),
        "processed_root": str(processed_root),
        "checkpoint_path": str(checkpoint_path),
        "metrics_path": str(metrics_path),
        "onnx_path": str(onnx_path) if onnx_prediction is not None else None,
        "summary_path": str(summary_path),
        "processed_counts": processed_counts,
        "train_result": train_result,
        "metrics": metrics,
        "sample_image": str(image_path),
        "pytorch_prediction": pytorch_prediction,
        "onnx_prediction": onnx_prediction,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Done. Wrote summary to {summary_path}")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a quick lane-classification smoke pipeline.")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--smoke", action="store_true", help="Run the fast synthetic-data smoke pipeline.")
    parser.add_argument("--epochs", type=_positive_int, default=1)
    parser.add_argument("--batch-size", type=_positive_int, default=2)
    parser.add_argument("--lr", type=_positive_float, default=1e-3)
    parser.add_argument("--image-size", type=_positive_int, default=32)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-count", type=_positive_int, default=4)
    parser.add_argument("--val-count", type=_positive_int, default=2)
    parser.add_argument("--skip-onnx", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.smoke:
        parser.error("currently only --smoke is supported; pass --smoke to run the quick verification pipeline")

    run_pipeline(
        PipelineConfig(
            workspace=args.workspace,
            smoke=args.smoke,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            image_size=args.image_size,
            device=args.device,
            seed=args.seed,
            train_count=args.train_count,
            val_count=args.val_count,
            skip_onnx=args.skip_onnx,
        )
    )
    return 0


def _prepare_smoke_dataset(
    raw_root: Path,
    processed_root: Path,
    train_annotations: Path,
    val_annotations: Path,
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for split, annotations_path in (("train", train_annotations), ("val", val_annotations)):
        inside_samples = prepare_tusimple_dataset(
            annotations_path=annotations_path,
            image_root=raw_root,
            output_root=processed_root,
            split=split,
        )
        outside_samples = prepare_tusimple_dataset(
            annotations_path=annotations_path,
            image_root=raw_root,
            output_root=processed_root,
            split=split,
            roi=(0, 35, 12, 61),
        )
        counts[split] = {
            "inside": sum(sample.label == "inside" for sample in inside_samples),
            "outside": sum(sample.label == "outside" for sample in outside_samples),
        }
        for class_name, count in counts[split].items():
            if count == 0:
                raise RuntimeError(f"smoke dataset has no {split}/{class_name} samples")
    return counts


def _pick_validation_image(val_dir: Path) -> Path:
    for class_name in ("inside", "outside"):
        image_path = next((val_dir / class_name).glob("*.jpg"), None)
        if image_path is not None:
            return image_path
    raise RuntimeError(f"no validation images found under {val_dir}")


def _validate_config(config: PipelineConfig) -> None:
    if config.epochs <= 0:
        raise ValueError("epochs must be positive")
    if config.batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if config.lr <= 0:
        raise ValueError("lr must be positive")
    if config.image_size <= 0:
        raise ValueError("image_size must be positive")
    if config.train_count <= 0:
        raise ValueError("train_count must be positive")
    if config.val_count <= 0:
        raise ValueError("val_count must be positive")


def _jsonable_config(config: PipelineConfig) -> dict:
    raw = asdict(config)
    raw["workspace"] = str(config.workspace)
    return raw


if __name__ == "__main__":
    raise SystemExit(main())
