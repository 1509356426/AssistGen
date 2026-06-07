import json
from pathlib import Path

import onnx
import pytest
import torch
from PIL import Image
from torch import nn

import lane_classification.export_onnx as export_onnx_module
import lane_classification.infer_onnx as infer_onnx_module
from lane_classification.checkpoint import save_checkpoint
from lane_classification.export_onnx import export_checkpoint_to_onnx, main as export_main
from lane_classification.infer_onnx import main as infer_onnx_main, predict_onnx_image


class TinyOnnxModel(nn.Module):
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


def test_export_checkpoint_to_onnx_writes_valid_dynamic_graph(tmp_path: Path) -> None:
    checkpoint_path = save_checkpoint(TinyOnnxModel(), tmp_path / "model.pt")
    output_path = tmp_path / "exports" / "model.onnx"

    result = export_checkpoint_to_onnx(
        checkpoint_path=checkpoint_path,
        output_path=output_path,
        image_size=16,
        opset=12,
        model_factory=TinyOnnxModel,
    )

    exported = onnx.load(str(output_path))
    onnx.checker.check_model(exported)
    assert result == output_path
    assert output_path.is_file()
    assert exported.graph.input[0].name == "input"
    assert exported.graph.output[0].name == "logits"
    assert exported.graph.input[0].type.tensor_type.shape.dim[0].dim_param == "batch"
    assert exported.graph.output[0].type.tensor_type.shape.dim[0].dim_param == "batch"


def test_export_checkpoint_to_onnx_validates_arguments(tmp_path: Path) -> None:
    checkpoint_path = save_checkpoint(TinyOnnxModel(), tmp_path / "model.pt")
    with pytest.raises(ValueError, match="image_size"):
        export_checkpoint_to_onnx(checkpoint_path, tmp_path / "model.onnx", image_size=0)
    with pytest.raises(ValueError, match="opset"):
        export_checkpoint_to_onnx(checkpoint_path, tmp_path / "model.onnx", opset=0)
    with pytest.raises(FileNotFoundError, match="Checkpoint does not exist"):
        export_checkpoint_to_onnx(tmp_path / "missing.pt", tmp_path / "model.onnx")
    with pytest.raises(IsADirectoryError, match="Output path is a directory"):
        export_checkpoint_to_onnx(checkpoint_path, tmp_path, model_factory=TinyOnnxModel)


def test_export_onnx_cli_success_path_delegates_to_core_function(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    checkpoint_path = tmp_path / "model.pt"
    checkpoint_path.write_bytes(b"checkpoint")
    output_path = tmp_path / "model.onnx"

    def fake_export(**kwargs: object) -> Path:
        assert kwargs["checkpoint_path"] == checkpoint_path
        assert kwargs["output_path"] == output_path
        assert kwargs["image_size"] == 32
        assert kwargs["opset"] == 13
        assert kwargs["device"] == "cpu"
        output_path.write_bytes(b"onnx")
        return output_path

    monkeypatch.setattr(export_onnx_module, "export_checkpoint_to_onnx", fake_export)

    assert export_main(
        [
            "--checkpoint",
            str(checkpoint_path),
            "--output",
            str(output_path),
            "--image-size",
            "32",
            "--opset",
            "13",
        ]
    ) == 0
    assert f"exported ONNX model to {output_path}" in capsys.readouterr().out


def test_export_onnx_cli_validation_errors_are_clear(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        export_main(["--checkpoint", str(tmp_path / "missing.pt"), "--output", str(tmp_path / "model.onnx")])
    assert "--checkpoint must be an existing file" in capsys.readouterr().err

    checkpoint_path = tmp_path / "model.pt"
    checkpoint_path.write_bytes(b"checkpoint")
    with pytest.raises(SystemExit):
        export_main(["--checkpoint", str(checkpoint_path), "--output", str(tmp_path)])
    assert "--output must be a file path" in capsys.readouterr().err

    with pytest.raises(SystemExit):
        export_main(["--checkpoint", str(checkpoint_path), "--output", str(tmp_path / "model.onnx"), "--opset", "0"])


def test_predict_onnx_image_returns_label_confidence_and_probabilities(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = TinyOnnxModel()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
        model.classifier.bias.copy_(torch.tensor([0.0, 3.0]))
    checkpoint_path = save_checkpoint(model, tmp_path / "model.pt")
    onnx_path = export_checkpoint_to_onnx(
        checkpoint_path=checkpoint_path,
        output_path=tmp_path / "model.onnx",
        image_size=16,
        model_factory=TinyOnnxModel,
    )
    image_path = tmp_path / "image.png"
    Image.new("RGB", (12, 10), (200, 200, 200)).save(image_path)
    transform_calls: list[int] = []
    real_get_eval_transform = infer_onnx_module.get_eval_transform

    def spy_get_eval_transform(image_size: int):
        transform_calls.append(image_size)
        return real_get_eval_transform(image_size)

    monkeypatch.setattr(infer_onnx_module, "get_eval_transform", spy_get_eval_transform)

    prediction = predict_onnx_image(onnx_path, image_path, image_size=16)

    assert transform_calls == [16]
    assert prediction["label"] == "inside"
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert prediction["confidence"] == pytest.approx(prediction["probabilities"]["inside"])
    assert prediction["confidence"] == pytest.approx(max(prediction["probabilities"].values()))
    assert set(prediction["probabilities"]) == {"outside", "inside"}
    assert all(0.0 <= probability <= 1.0 for probability in prediction["probabilities"].values())
    assert sum(prediction["probabilities"].values()) == pytest.approx(1.0)


def test_predict_onnx_image_validates_arguments(tmp_path: Path) -> None:
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"onnx")
    image_path = tmp_path / "image.png"
    Image.new("RGB", (12, 10), (200, 200, 200)).save(image_path)

    with pytest.raises(ValueError, match="image_size"):
        predict_onnx_image(model_path, image_path, image_size=0)
    with pytest.raises(FileNotFoundError, match="ONNX model does not exist"):
        predict_onnx_image(tmp_path / "missing.onnx", image_path)
    with pytest.raises(FileNotFoundError, match="Image does not exist"):
        predict_onnx_image(model_path, tmp_path / "missing.png")


def test_infer_onnx_cli_success_path_emits_parseable_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"onnx")
    image_path = tmp_path / "image.png"
    Image.new("RGB", (12, 10), (200, 200, 200)).save(image_path)

    def fake_predict(**kwargs: object) -> dict:
        assert kwargs["model_path"] == model_path
        assert kwargs["image_path"] == image_path
        assert kwargs["image_size"] == 32
        assert kwargs["providers"] == ["CPUExecutionProvider"]
        return {
            "label": "inside",
            "confidence": 0.9,
            "probabilities": {"outside": 0.1, "inside": 0.9},
        }

    monkeypatch.setattr(infer_onnx_module, "predict_onnx_image", fake_predict)

    assert infer_onnx_main(
        [
            "--model",
            str(model_path),
            "--image",
            str(image_path),
            "--image-size",
            "32",
            "--provider",
            "CPUExecutionProvider",
        ]
    ) == 0
    assert json.loads(capsys.readouterr().out) == {
        "label": "inside",
        "confidence": 0.9,
        "probabilities": {"outside": 0.1, "inside": 0.9},
    }


def test_infer_onnx_cli_validation_errors_are_clear(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        infer_onnx_main(["--model", str(tmp_path / "missing.onnx"), "--image", str(tmp_path / "image.png")])
    assert "--model must be an existing file" in capsys.readouterr().err

    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"onnx")
    with pytest.raises(SystemExit):
        infer_onnx_main(["--model", str(model_path), "--image", str(tmp_path / "missing.png")])
    assert "--image must be an existing file" in capsys.readouterr().err
