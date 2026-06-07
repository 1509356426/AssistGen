import hashlib
from pathlib import Path

import pytest

from lane_classification.prepare_tusimple import parse_tusimple_jsonl, prepare_tusimple_dataset
from lane_classification.synthetic import generate_synthetic_tusimple, main


def test_generate_synthetic_tusimple_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_annotations = generate_synthetic_tusimple(first, split="train", count=3)
    second_annotations = generate_synthetic_tusimple(second, split="train", count=3)

    assert first_annotations.read_text(encoding="utf-8") == second_annotations.read_text(encoding="utf-8")
    assert _digest(first / "raw" / "train" / "sample_0000.jpg") == _digest(
        second / "raw" / "train" / "sample_0000.jpg"
    )


def test_synthetic_tusimple_can_be_prepared(tmp_path: Path) -> None:
    annotations_path = generate_synthetic_tusimple(tmp_path, split="train", count=2, image_size=(96, 64))

    annotations = parse_tusimple_jsonl(annotations_path)
    samples = prepare_tusimple_dataset(
        annotations_path=annotations_path,
        image_root=tmp_path,
        output_root=tmp_path / "processed",
        split="train",
    )

    assert len(annotations) == 2
    assert [sample.label for sample in samples] == ["inside", "inside"]
    assert len(list((tmp_path / "processed" / "train" / "inside").glob("*.jpg"))) == 2
    assert (tmp_path / "processed" / "train" / "outside").is_dir()


def test_generate_synthetic_tusimple_validates_inputs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="count must be positive"):
        generate_synthetic_tusimple(tmp_path / "bad_count", count=0)
    with pytest.raises(ValueError, match="image dimensions must be positive"):
        generate_synthetic_tusimple(tmp_path / "bad_size", image_size=(0, 64))


def test_synthetic_cli_writes_annotations(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(tmp_path), "--split", "val", "--count", "1", "--width", "32", "--height", "24"]) == 0

    assert "Wrote annotations" in capsys.readouterr().out
    assert (tmp_path / "val.jsonl").is_file()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
