from pathlib import Path

import pytest
import torch
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from torch import nn

from lane_classification.evaluate import evaluate_checkpoint
from lane_classification.export_onnx import export_checkpoint_to_onnx
from lane_classification.infer import predict_image
from lane_classification.infer_onnx import predict_onnx_image
from lane_classification.prepare_tusimple import prepare_tusimple_dataset
from lane_classification.synthetic import generate_synthetic_tusimple
from lane_classification.train import TrainingConfig, train_model


class TinyEndToEndModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 4, kernel_size=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(4, 2)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(images).flatten(1))


def test_synthetic_pipeline_generate_prepare_train_evaluate_and_infer(tmp_path: Path) -> None:
    raw_root = tmp_path / "synthetic"
    processed_root = tmp_path / "processed"
    train_annotations = generate_synthetic_tusimple(raw_root, split="train", count=2, image_size=(64, 48))
    eval_annotations = generate_synthetic_tusimple(raw_root, split="val", count=2, image_size=(64, 48))

    for split, annotations_path in (("train", train_annotations), ("val", eval_annotations)):
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
            roi=(0, 28, 8, 44),
        )
        assert {sample.label for sample in inside_samples} == {"inside"}
        assert {sample.label for sample in outside_samples} == {"outside"}

    checkpoint_path = tmp_path / "checkpoints" / "lane.pt"
    log_dir = tmp_path / "runs"
    train_result = train_model(
        TrainingConfig(
            train_dir=processed_root / "train",
            checkpoint_path=checkpoint_path,
            val_dir=processed_root / "val",
            log_dir=log_dir,
            epochs=1,
            batch_size=2,
            lr=0.01,
            image_size=16,
            seed=7,
        ),
        model_factory=TinyEndToEndModel,
    )

    assert checkpoint_path.is_file()
    assert train_result["checkpoint_path"] == str(checkpoint_path)
    assert train_result["history"][0]["epoch"] == 1
    assert set(train_result["history"][0]) >= {"train_loss", "train_accuracy", "val_loss", "val_accuracy"}

    assert list(log_dir.glob("events.out.tfevents.*"))
    event_accumulator = EventAccumulator(str(log_dir))
    event_accumulator.Reload()
    assert set(event_accumulator.Tags()["scalars"]) >= {
        "train/loss",
        "train/accuracy",
        "validation/loss",
        "validation/accuracy",
    }

    metrics_path = tmp_path / "metrics.json"
    metrics = evaluate_checkpoint(
        checkpoint_path=checkpoint_path,
        data_dir=processed_root / "val",
        batch_size=2,
        image_size=16,
        metrics_path=metrics_path,
        model_factory=TinyEndToEndModel,
    )

    assert metrics_path.is_file()
    assert metrics["num_samples"] == 4
    assert metrics["class_names"] == ["outside", "inside"]
    assert set(metrics) >= {"accuracy", "precision", "recall", "f1", "confusion_matrix"}
    assert 0.0 <= metrics["accuracy"] <= 1.0

    image_path = next((processed_root / "val" / "inside").glob("*.jpg"))
    prediction = predict_image(
        checkpoint_path=checkpoint_path,
        image_path=image_path,
        image_size=16,
        model_factory=TinyEndToEndModel,
    )

    assert prediction["label"] in {"outside", "inside"}
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert set(prediction["probabilities"]) == {"outside", "inside"}
    assert sum(prediction["probabilities"].values()) == pytest.approx(1.0)

    onnx_path = export_checkpoint_to_onnx(
        checkpoint_path=checkpoint_path,
        output_path=tmp_path / "exports" / "lane.onnx",
        image_size=16,
        model_factory=TinyEndToEndModel,
    )
    onnx_prediction = predict_onnx_image(onnx_path, image_path, image_size=16)

    assert onnx_path.is_file()
    assert onnx_prediction["label"] in {"outside", "inside"}
    assert 0.0 <= onnx_prediction["confidence"] <= 1.0
    assert set(onnx_prediction["probabilities"]) == {"outside", "inside"}
    assert all(0.0 <= probability <= 1.0 for probability in onnx_prediction["probabilities"].values())
    assert sum(onnx_prediction["probabilities"].values()) == pytest.approx(1.0)
    assert onnx_prediction["confidence"] == pytest.approx(
        onnx_prediction["probabilities"][onnx_prediction["label"]]
    )
