from __future__ import annotations

import argparse
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence

import torch
from torch import nn
from torch.utils.data import DataLoader

from lane_classification.checkpoint import DEFAULT_CLASS_NAMES, save_checkpoint
from lane_classification.dataset import LaneClassificationDataset
from lane_classification.model import create_resnet18_binary_model
from lane_classification.transforms import get_eval_transform, get_train_transform


@dataclass(frozen=True)
class TrainingConfig:
    train_dir: Path
    checkpoint_path: Path
    epochs: int = 1
    batch_size: int = 8
    lr: float = 1e-3
    device: str = "cpu"
    image_size: int = 224
    num_workers: int = 0
    seed: int = 0
    val_dir: Path | None = None
    log_dir: Path | None = None


def train_model(
    config: TrainingConfig,
    model_factory: Callable[[], nn.Module] = create_resnet18_binary_model,
) -> dict:
    _validate_training_config(config)
    _seed_everything(config.seed)
    device = torch.device(config.device)
    dataset = LaneClassificationDataset(
        config.train_dir,
        transform=get_train_transform(config.image_size),
    )
    loader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
    )
    val_loader = _build_validation_loader(config)
    model = model_factory().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    criterion = nn.CrossEntropyLoss()
    history: list[dict] = []
    writer = _create_summary_writer(config.log_dir)

    try:
        for epoch in range(config.epochs):
            train_loss, train_accuracy = _train_one_epoch(
                model=model,
                loader=loader,
                optimizer=optimizer,
                criterion=criterion,
                device=device,
            )
            epoch_metrics = {
                "epoch": epoch + 1,
                "loss": train_loss,
                "accuracy": train_accuracy,
                "train_loss": train_loss,
                "train_accuracy": train_accuracy,
            }
            _write_scalar_metrics(
                writer,
                epoch + 1,
                {
                    "train/loss": train_loss,
                    "train/accuracy": train_accuracy,
                },
            )
            if val_loader is not None:
                val_loss, val_accuracy = _evaluate_loader(
                    model=model,
                    loader=val_loader,
                    criterion=criterion,
                    device=device,
                )
                epoch_metrics["val_loss"] = val_loss
                epoch_metrics["val_accuracy"] = val_accuracy
                _write_scalar_metrics(
                    writer,
                    epoch + 1,
                    {
                        "validation/loss": val_loss,
                        "validation/accuracy": val_accuracy,
                    },
                )
            history.append(epoch_metrics)
    finally:
        if writer is not None:
            writer.close()

    save_checkpoint(
        model,
        config.checkpoint_path,
        class_names=DEFAULT_CLASS_NAMES,
        metadata={"training_config": _jsonable_config(config), "history": history},
    )
    return {"checkpoint_path": str(config.checkpoint_path), "history": history}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a lane inside/outside classifier.")
    parser.add_argument("--train-dir", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--val-dir", type=Path)
    parser.add_argument("--log-dir", type=Path)
    parser.add_argument("--epochs", type=_positive_int, default=1)
    parser.add_argument("--batch-size", type=_positive_int, default=8)
    parser.add_argument("--lr", type=_positive_float, default=1e-3)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--image-size", type=_positive_int, default=224)
    parser.add_argument("--num-workers", type=_non_negative_int, default=0)
    parser.add_argument("--seed", type=int, default=0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.train_dir.is_dir():
        parser.error(f"--train-dir must be an existing directory: {args.train_dir}")
    if args.val_dir is not None and not args.val_dir.is_dir():
        parser.error(f"--val-dir must be an existing directory: {args.val_dir}")

    result = train_model(
        TrainingConfig(
            train_dir=args.train_dir,
            checkpoint_path=args.checkpoint,
            val_dir=args.val_dir,
            log_dir=args.log_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            device=args.device,
            image_size=args.image_size,
            num_workers=args.num_workers,
            seed=args.seed,
        )
    )
    last_epoch = result["history"][-1]
    print(
        f"saved checkpoint to {result['checkpoint_path']} "
        f"loss={last_epoch['loss']:.4f} accuracy={last_epoch['accuracy']:.4f}"
    )
    return 0


def _validate_training_config(config: TrainingConfig) -> None:
    if config.epochs <= 0:
        raise ValueError("epochs must be positive")
    if config.batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if config.lr <= 0:
        raise ValueError("lr must be positive")
    if config.image_size <= 0:
        raise ValueError("image_size must be positive")
    if config.num_workers < 0:
        raise ValueError("num_workers cannot be negative")


def _build_validation_loader(config: TrainingConfig) -> DataLoader | None:
    if config.val_dir is None:
        return None
    dataset = LaneClassificationDataset(
        config.val_dir,
        transform=get_eval_transform(config.image_size),
    )
    return DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
    )


def _train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.train()
    total_loss = 0.0
    correct = 0
    seen = 0
    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        batch_size = labels.size(0)
        total_loss += loss.item() * batch_size
        correct += (logits.argmax(dim=1) == labels).sum().item()
        seen += batch_size
    return total_loss / seen, correct / seen


def _evaluate_loader(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()
    total_loss = 0.0
    correct = 0
    seen = 0
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)

            batch_size = labels.size(0)
            total_loss += loss.item() * batch_size
            correct += (logits.argmax(dim=1) == labels).sum().item()
            seen += batch_size
    return total_loss / seen, correct / seen


def _create_summary_writer(log_dir: Path | None):
    if log_dir is None:
        return None
    from torch.utils.tensorboard import SummaryWriter

    return SummaryWriter(log_dir=str(log_dir))


def _write_scalar_metrics(writer, epoch: int, metrics: dict[str, float]) -> None:
    if writer is None:
        return
    for tag, value in metrics.items():
        writer.add_scalar(tag, value, epoch)


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)


def _jsonable_config(config: TrainingConfig) -> dict:
    raw = asdict(config)
    raw["train_dir"] = str(config.train_dir)
    raw["checkpoint_path"] = str(config.checkpoint_path)
    if raw["val_dir"] is not None:
        raw["val_dir"] = str(config.val_dir)
    if raw["log_dir"] is not None:
        raw["log_dir"] = str(config.log_dir)
    return raw


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("cannot be negative")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
