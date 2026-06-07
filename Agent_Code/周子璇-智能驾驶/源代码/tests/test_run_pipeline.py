from pathlib import Path

import pytest
import torch
from torch import nn

from lane_classification.run_pipeline import PipelineConfig, main, run_pipeline


class TinyPipelineModel(nn.Module):
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


def test_run_pipeline_smoke_completes(tmp_path: Path) -> None:
    summary = run_pipeline(
        PipelineConfig(
            workspace=tmp_path / "smoke",
            smoke=True,
            epochs=1,
            batch_size=2,
            lr=0.01,
            image_size=16,
            seed=3,
            train_count=2,
            val_count=2,
            skip_onnx=True,
        ),
        model_factory=TinyPipelineModel,
    )

    workspace = tmp_path / "smoke"
    assert (workspace / "checkpoints" / "lane.pt").is_file()
    assert (workspace / "metrics.json").is_file()
    assert (workspace / "summary.json").is_file()
    assert summary["checkpoint_path"] == str(workspace / "checkpoints" / "lane.pt")
    assert summary["metrics_path"] == str(workspace / "metrics.json")
    assert summary["onnx_prediction"] is None
    assert set(summary) >= {"metrics", "pytorch_prediction", "train_result"}
    assert summary["metrics"]["num_samples"] == 4
    assert summary["pytorch_prediction"]["label"] in {"outside", "inside"}

    for split in ("train", "val"):
        for class_name in ("inside", "outside"):
            assert list((workspace / "processed" / split / class_name).glob("*.jpg"))
            assert summary["processed_counts"][split][class_name] > 0


def test_run_pipeline_cli_requires_smoke(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--workspace", str(tmp_path / "smoke")])

    assert exc_info.value.code == 2
    assert "only --smoke is supported" in capsys.readouterr().err
