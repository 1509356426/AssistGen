from pathlib import Path

import pytest
import torch
from PIL import Image
from torch import nn
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

from lane_classification.checkpoint import load_checkpoint, save_checkpoint
import lane_classification.evaluate as evaluate_module
import lane_classification.infer as infer_module
import lane_classification.train as train_module
from lane_classification.evaluate import evaluate_checkpoint, main as evaluate_main
from lane_classification.infer import main as infer_main, predict_image
from lane_classification.metrics import compute_binary_metrics
from lane_classification.train import TrainingConfig, main as train_main, train_model


class TinyTrainModel(nn.Module):
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


class ConstantModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.logits = nn.Parameter(torch.tensor([0.0, 3.0]))

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.logits.unsqueeze(0).expand(images.size(0), -1)


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (12, 10), color=color).save(path)


def _write_split(root: Path) -> Path:
    split_dir = root / "train"
    _write_image(split_dir / "outside" / "outside_0.png", (20, 20, 20))
    _write_image(split_dir / "outside" / "outside_1.png", (25, 25, 25))
    _write_image(split_dir / "inside" / "inside_0.png", (220, 220, 220))
    _write_image(split_dir / "inside" / "inside_1.png", (230, 230, 230))
    return split_dir


def test_train_model_saves_reloadable_checkpoint(tmp_path: Path) -> None:
    split_dir = _write_split(tmp_path)
    checkpoint_path = tmp_path / "model.pt"

    result = train_model(
        TrainingConfig(
            train_dir=split_dir,
            checkpoint_path=checkpoint_path,
            epochs=1,
            batch_size=2,
            lr=0.01,
            image_size=16,
        ),
        model_factory=TinyTrainModel,
    )

    model, class_names, checkpoint = load_checkpoint(checkpoint_path, model_factory=TinyTrainModel)
    assert checkpoint_path.is_file()
    assert result["history"][0]["epoch"] == 1
    assert class_names == ["outside", "inside"]
    assert checkpoint["metadata"]["training_config"]["batch_size"] == 2
    with torch.no_grad():
        assert model(torch.randn(1, 3, 16, 16)).shape == (1, 2)


def test_train_model_computes_validation_metrics(tmp_path: Path) -> None:
    split_dir = _write_split(tmp_path)
    val_dir = tmp_path / "val"
    _write_image(val_dir / "outside" / "outside_0.png", (30, 30, 30))
    _write_image(val_dir / "inside" / "inside_0.png", (210, 210, 210))

    result = train_model(
        TrainingConfig(
            train_dir=split_dir,
            checkpoint_path=tmp_path / "model.pt",
            val_dir=val_dir,
            epochs=1,
            batch_size=2,
            lr=0.01,
            image_size=16,
        ),
        model_factory=TinyTrainModel,
    )

    epoch = result["history"][0]
    assert set(epoch) >= {"train_loss", "train_accuracy", "val_loss", "val_accuracy"}
    assert epoch["loss"] == epoch["train_loss"]
    assert epoch["accuracy"] == epoch["train_accuracy"]
    assert 0.0 <= epoch["train_accuracy"] <= 1.0
    assert 0.0 <= epoch["val_accuracy"] <= 1.0


def test_train_model_writes_tensorboard_scalars_only_when_requested(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    split_dir = _write_split(tmp_path)
    log_dir = tmp_path / "runs"
    calls: list[Path | None] = []
    real_create_writer = train_module._create_summary_writer

    def spy_create_writer(path: Path | None):
        calls.append(path)
        return real_create_writer(path)

    monkeypatch.setattr(train_module, "_create_summary_writer", spy_create_writer)
    train_model(
        TrainingConfig(
            train_dir=split_dir,
            checkpoint_path=tmp_path / "model.pt",
            epochs=1,
            batch_size=2,
            lr=0.01,
            image_size=16,
        ),
        model_factory=TinyTrainModel,
    )
    assert calls == [None]
    assert not log_dir.exists()

    val_dir = tmp_path / "val"
    _write_image(val_dir / "outside" / "outside_0.png", (30, 30, 30))
    _write_image(val_dir / "inside" / "inside_0.png", (210, 210, 210))
    train_model(
        TrainingConfig(
            train_dir=split_dir,
            checkpoint_path=tmp_path / "logged.pt",
            val_dir=val_dir,
            log_dir=log_dir,
            epochs=1,
            batch_size=2,
            lr=0.01,
            image_size=16,
        ),
        model_factory=TinyTrainModel,
    )

    event_files = list(log_dir.glob("events.out.tfevents.*"))
    assert calls[-1] == log_dir
    assert event_files
    event_accumulator = EventAccumulator(str(log_dir))
    event_accumulator.Reload()
    assert set(event_accumulator.Tags()["scalars"]) >= {
        "train/loss",
        "train/accuracy",
        "validation/loss",
        "validation/accuracy",
    }


def test_evaluate_checkpoint_computes_and_writes_metrics(tmp_path: Path) -> None:
    split_dir = _write_split(tmp_path)
    checkpoint_path = save_checkpoint(ConstantModel(), tmp_path / "constant.pt")
    metrics_path = tmp_path / "metrics.json"

    metrics = evaluate_checkpoint(
        checkpoint_path=checkpoint_path,
        data_dir=split_dir,
        batch_size=2,
        image_size=16,
        metrics_path=metrics_path,
        model_factory=ConstantModel,
    )

    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == pytest.approx(2 / 3)
    assert metrics["confusion_matrix"] == [[0, 2], [0, 2]]
    assert '"num_samples": 4' in metrics_path.read_text(encoding="utf-8")


def test_predict_image_returns_label_confidence_and_probabilities(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    _write_image(image_path, (200, 200, 200))
    checkpoint_path = save_checkpoint(ConstantModel(), tmp_path / "constant.pt")

    prediction = predict_image(
        checkpoint_path=checkpoint_path,
        image_path=image_path,
        image_size=16,
        model_factory=ConstantModel,
    )

    assert prediction["label"] == "inside"
    assert prediction["confidence"] == pytest.approx(prediction["probabilities"]["inside"])
    assert sum(prediction["probabilities"].values()) == pytest.approx(1.0)


def test_compute_binary_metrics_validates_inputs() -> None:
    assert compute_binary_metrics([0, 1], [0, 1])["confusion_matrix"] == [[1, 0], [0, 1]]
    with pytest.raises(ValueError, match="same length"):
        compute_binary_metrics([0], [0, 1])
    with pytest.raises(ValueError, match="at least one"):
        compute_binary_metrics([], [])
    with pytest.raises(ValueError, match="labels 0 or 1"):
        compute_binary_metrics([2], [1])


def test_checkpoint_validation_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Checkpoint does not exist"):
        load_checkpoint(tmp_path / "missing.pt")
    with pytest.raises(ValueError, match="exactly two"):
        save_checkpoint(ConstantModel(), tmp_path / "bad.pt", class_names=["inside"])
    bad_path = tmp_path / "invalid.pt"
    torch.save({"class_names": ["outside", "inside"]}, bad_path)
    with pytest.raises(ValueError, match="model_state_dict"):
        load_checkpoint(bad_path, model_factory=ConstantModel)


def test_core_functions_validate_numeric_arguments(tmp_path: Path) -> None:
    split_dir = _write_split(tmp_path)
    with pytest.raises(ValueError, match="epochs"):
        train_model(TrainingConfig(split_dir, tmp_path / "x.pt", epochs=0), model_factory=TinyTrainModel)
    with pytest.raises(ValueError, match="batch_size"):
        evaluate_checkpoint(tmp_path / "x.pt", split_dir, batch_size=0, model_factory=TinyTrainModel)
    with pytest.raises(ValueError, match="image_size"):
        predict_image(tmp_path / "x.pt", split_dir / "inside" / "inside_0.png", image_size=0)


def test_cli_validation_errors_are_clear(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        train_main(["--train-dir", str(tmp_path / "missing"), "--checkpoint", str(tmp_path / "x.pt")])
    assert "--train-dir must be an existing directory" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        train_main(
            [
                "--train-dir",
                str(tmp_path),
                "--checkpoint",
                str(tmp_path / "x.pt"),
                "--val-dir",
                str(tmp_path / "missing-val"),
            ]
        )
    assert "--val-dir must be an existing directory" in capsys.readouterr().err

    with pytest.raises(SystemExit):
        evaluate_main(["--checkpoint", str(tmp_path / "missing.pt"), "--data-dir", str(tmp_path)])
    assert "--checkpoint must be an existing file" in capsys.readouterr().err

    with pytest.raises(SystemExit):
        infer_main(["--checkpoint", str(tmp_path / "missing.pt"), "--image", str(tmp_path / "x.png")])
    assert "--checkpoint must be an existing file" in capsys.readouterr().err


def test_cli_success_paths_delegate_to_core_functions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    split_dir = _write_split(tmp_path)
    checkpoint_path = tmp_path / "model.pt"
    checkpoint_path.write_bytes(b"checkpoint")
    image_path = split_dir / "inside" / "inside_0.png"

    def fake_train(config: TrainingConfig) -> dict:
        assert config.train_dir == split_dir
        assert config.val_dir == split_dir
        assert config.log_dir == tmp_path / "runs"
        assert config.batch_size == 3
        return {"checkpoint_path": str(config.checkpoint_path), "history": [{"loss": 0.5, "accuracy": 0.75}]}

    def fake_evaluate(**kwargs: object) -> dict:
        assert kwargs["checkpoint_path"] == checkpoint_path
        assert kwargs["data_dir"] == split_dir
        return {"accuracy": 1.0}

    def fake_predict(**kwargs: object) -> dict:
        assert kwargs["checkpoint_path"] == checkpoint_path
        assert kwargs["image_path"] == image_path
        return {"label": "inside", "confidence": 0.9}

    monkeypatch.setattr(train_module, "train_model", fake_train)
    monkeypatch.setattr(evaluate_module, "evaluate_checkpoint", fake_evaluate)
    monkeypatch.setattr(infer_module, "predict_image", fake_predict)

    assert train_main(
        [
            "--train-dir",
            str(split_dir),
            "--checkpoint",
            str(tmp_path / "trained.pt"),
            "--batch-size",
            "3",
            "--val-dir",
            str(split_dir),
            "--log-dir",
            str(tmp_path / "runs"),
        ]
    ) == 0
    assert "saved checkpoint" in capsys.readouterr().out
    assert evaluate_main(["--checkpoint", str(checkpoint_path), "--data-dir", str(split_dir)]) == 0
    assert '"accuracy": 1.0' in capsys.readouterr().out
    assert infer_main(["--checkpoint", str(checkpoint_path), "--image", str(image_path)]) == 0
    assert '"label": "inside"' in capsys.readouterr().out


def test_cli_numeric_type_validation(tmp_path: Path) -> None:
    split_dir = _write_split(tmp_path)
    with pytest.raises(SystemExit):
        train_main(
            [
                "--train-dir",
                str(split_dir),
                "--checkpoint",
                str(tmp_path / "x.pt"),
                "--lr",
                "0",
            ]
        )
    with pytest.raises(SystemExit):
        train_main(
            [
                "--train-dir",
                str(split_dir),
                "--checkpoint",
                str(tmp_path / "x.pt"),
                "--num-workers",
                "-1",
            ]
        )
