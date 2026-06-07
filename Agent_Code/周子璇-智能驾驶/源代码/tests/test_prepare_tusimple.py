import json
from pathlib import Path

import pytest
from PIL import Image

import lane_classification.prepare_tusimple as prepare_module
from lane_classification.prepare_tusimple import (
    CLASS_TO_INDEX,
    TusimpleAnnotation,
    build_arg_parser,
    bound_roi,
    classify_roi_center,
    default_roi,
    interpolate_lane_x,
    main,
    parse_tusimple_jsonl,
    prepare_tusimple_dataset,
)


def test_class_order_is_fixed() -> None:
    assert CLASS_TO_INDEX == {"outside": 0, "inside": 1}


def test_parse_tusimple_jsonl_and_reject_missing_fields(tmp_path: Path) -> None:
    path = tmp_path / "labels.jsonl"
    path.write_text(
        json.dumps({"raw_file": "a.jpg", "lanes": [[1, -2, 3]], "h_samples": [10, 20, 30]})
        + "\n",
        encoding="utf-8",
    )

    annotations = parse_tusimple_jsonl(path)

    assert annotations == [
        TusimpleAnnotation(raw_file="a.jpg", lanes=[[1.0, -2.0, 3.0]], h_samples=[10.0, 20.0, 30.0])
    ]

    bad_path = tmp_path / "bad.jsonl"
    bad_path.write_text(json.dumps({"raw_file": "a.jpg", "lanes": []}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing fields: h_samples"):
        parse_tusimple_jsonl(bad_path)


def test_parse_tusimple_jsonl_rejects_malformed_records(tmp_path: Path) -> None:
    bad_json = tmp_path / "bad_json.jsonl"
    bad_json.write_text("{bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        parse_tusimple_jsonl(bad_json)

    cases = [
        ({"raw_file": 1, "lanes": [], "h_samples": []}, "raw_file must be a string"),
        ({"raw_file": "a.jpg", "lanes": [1], "h_samples": []}, "lanes must be a list of lists"),
        ({"raw_file": "a.jpg", "lanes": [], "h_samples": "bad"}, "h_samples must be a list"),
        (
            {"raw_file": "a.jpg", "lanes": [[1, 2]], "h_samples": [1]},
            "lane 0 length does not match h_samples",
        ),
        (
            {"raw_file": "a.jpg", "lanes": [[True]], "h_samples": [1]},
            "lanes\\[0\\] values must be numeric",
        ),
    ]
    for index, (record, message) in enumerate(cases):
        path = tmp_path / f"case_{index}.jsonl"
        path.write_text(json.dumps(record), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            parse_tusimple_jsonl(path)


def test_interpolate_lane_x_ignores_invalid_values() -> None:
    assert interpolate_lane_x([-2, 20, 30], [10, 20, 30], 25) == 25
    assert interpolate_lane_x([-2, -2], [10, 20], 15) is None


def test_default_roi_is_lower_middle_and_bounded() -> None:
    assert default_roi((100, 80)) == (25, 44, 75, 76)
    assert default_roi((3, 3)) == (1, 2, 2, 3)
    with pytest.raises(ValueError, match="image dimensions must be positive"):
        default_roi((0, 3))
    with pytest.raises(ValueError, match="roi must contain"):
        bound_roi((1, 2, 3), (10, 10))
    with pytest.raises(ValueError, match="roi is empty"):
        bound_roi((5, 5, 5, 6), (10, 10))


def test_classify_roi_center_uses_nearest_boundaries_around_image_center() -> None:
    annotation = TusimpleAnnotation(
        raw_file="a.jpg",
        lanes=[[10, 20, 30], [70, 80, 90], [2, 2, 2], [95, 95, 95]],
        h_samples=[20, 40, 60],
    )

    assert classify_roi_center(annotation, (100, 80), roi=(40, 40, 60, 60)) == "inside"
    assert classify_roi_center(annotation, (100, 80), roi=(0, 40, 10, 60)) == "outside"
    assert classify_roi_center(
        TusimpleAnnotation(raw_file="a.jpg", lanes=[[10, 20, 30]], h_samples=[20, 40, 60]),
        (100, 80),
    ) is None


def test_prepare_tusimple_dataset_writes_processed_layout_and_skips_unusable(tmp_path: Path) -> None:
    image_root = tmp_path / "dataset"
    image_root.mkdir()
    Image.new("RGB", (100, 80), (10, 20, 30)).save(image_root / "inside.jpg")
    Image.new("RGB", (100, 80), (30, 20, 10)).save(image_root / "skip.jpg")
    annotations = image_root / "train.jsonl"
    records = [
        {"raw_file": "inside.jpg", "lanes": [[20, 20, 20], [80, 80, 80]], "h_samples": [20, 50, 70]},
        {"raw_file": "skip.jpg", "lanes": [[20, 20, 20]], "h_samples": [20, 50, 70]},
    ]
    annotations.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    samples = prepare_tusimple_dataset(
        annotations_path=annotations,
        output_root=tmp_path / "processed",
        split="train",
        mode="fixed",
    )

    assert [sample.label for sample in samples] == ["inside"]
    assert samples[0].roi == (25, 44, 75, 76)
    assert samples[0].output_path == tmp_path / "processed" / "train" / "inside" / "inside_0001.jpg"
    assert samples[0].output_path.exists()
    assert (tmp_path / "processed" / "train" / "outside").is_dir()


def test_prepare_tusimple_dataset_can_write_outside_with_explicit_roi(tmp_path: Path) -> None:
    Image.new("RGB", (100, 80), (10, 20, 30)).save(tmp_path / "sample.jpg")
    annotations = tmp_path / "train.jsonl"
    annotations.write_text(
        json.dumps({"raw_file": "sample.jpg", "lanes": [[20, 20, 20], [80, 80, 80]], "h_samples": [20, 50, 70]}),
        encoding="utf-8",
    )

    samples = prepare_tusimple_dataset(
        annotations_path=annotations,
        output_root=tmp_path / "processed",
        split="val",
        roi=(0, 40, 10, 70),
    )

    assert [sample.label for sample in samples] == ["outside"]
    assert (tmp_path / "processed" / "val" / "outside" / "sample_0001.jpg").exists()


def test_prepare_tusimple_dataset_dynamic_writes_inside_and_outside_left(tmp_path: Path) -> None:
    Image.new("RGB", (200, 120), (10, 20, 30)).save(tmp_path / "sample.jpg")
    annotations = tmp_path / "train.jsonl"
    annotations.write_text(
        json.dumps({"raw_file": "sample.jpg", "lanes": [[80, 80, 80], [120, 120, 120]], "h_samples": [40, 60, 80]}),
        encoding="utf-8",
    )

    samples = prepare_tusimple_dataset(
        annotations_path=annotations,
        output_root=tmp_path / "processed",
        split="train",
        mode="dynamic",
        roi_width=40,
        roi_height=30,
        target_y=60,
        outside_side="left",
    )

    assert [sample.label for sample in samples] == ["inside", "outside"]
    assert samples[0].roi == (80, 45, 120, 75)
    assert samples[1].roi == (58, 45, 98, 75)
    assert samples[0].output_path.name == "sample_0001_inside.jpg"
    assert samples[1].output_path.name == "sample_0001_outside_left.jpg"
    for sample in samples:
        with Image.open(sample.output_path) as image:
            assert image.size == (40, 30)


def test_prepare_tusimple_dataset_dynamic_uses_nearest_valid_outside_centers(tmp_path: Path) -> None:
    Image.new("RGB", (100, 80), (10, 20, 30)).save(tmp_path / "sample.jpg")
    annotations = tmp_path / "train.jsonl"
    annotations.write_text(
        json.dumps({"raw_file": "sample.jpg", "lanes": [[35, 35, 35], [65, 65, 65]], "h_samples": [20, 40, 60]}),
        encoding="utf-8",
    )

    samples = prepare_tusimple_dataset(
        annotations_path=annotations,
        output_root=tmp_path / "processed",
        split="train",
        mode="dynamic",
        roi_width=60,
        roi_height=20,
        target_y=40,
        outside_offset_ratio=0.35,
        outside_side="both",
    )

    assert [sample.label for sample in samples] == ["inside", "outside", "outside"]
    assert [sample.roi for sample in samples] == [(20, 30, 80, 50), (0, 30, 60, 50), (40, 30, 100, 50)]
    assert len(list((tmp_path / "processed" / "train" / "outside").glob("*.jpg"))) == 2
    for sample in samples:
        with Image.open(sample.output_path) as image:
            assert image.size == (60, 20)


def test_prepare_tusimple_dataset_dynamic_skips_outside_when_classification_disagrees(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    Image.new("RGB", (100, 80), (10, 20, 30)).save(tmp_path / "sample.jpg")
    annotations = tmp_path / "train.jsonl"
    annotations.write_text(
        json.dumps({"raw_file": "sample.jpg", "lanes": [[35, 35, 35], [65, 65, 65]], "h_samples": [20, 40, 60]}),
        encoding="utf-8",
    )

    def fake_classify(
        annotation: TusimpleAnnotation,
        image_size: tuple[int, int],
        roi: tuple[int, int, int, int] | None = None,
    ) -> str:
        return "inside"

    monkeypatch.setattr(prepare_module, "classify_roi_center", fake_classify)

    samples = prepare_tusimple_dataset(
        annotations_path=annotations,
        output_root=tmp_path / "processed",
        split="train",
        mode="dynamic",
        roi_width=60,
        roi_height=20,
        target_y=40,
        outside_side="both",
    )

    assert [sample.label for sample in samples] == ["inside"]
    assert not list((tmp_path / "processed" / "train" / "outside").glob("*.jpg"))


def test_prepare_cli_parser_accepts_dynamic_options(tmp_path: Path) -> None:
    args = build_arg_parser().parse_args(
        [
            str(tmp_path / "train.jsonl"),
            "--mode",
            "dynamic",
            "--roi-width",
            "40",
            "--roi-height",
            "30",
            "--target-y",
            "60.5",
            "--outside-offset-ratio",
            "0.25",
            "--outside-side",
            "both",
        ]
    )

    assert args.mode == "dynamic"
    assert args.roi_width == 40
    assert args.roi_height == 30
    assert args.target_y == 60.5
    assert args.outside_offset_ratio == 0.25
    assert args.outside_side == "both"


def test_prepare_cli_writes_samples(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    Image.new("RGB", (100, 80), (10, 20, 30)).save(tmp_path / "sample.jpg")
    annotations = tmp_path / "train.jsonl"
    annotations.write_text(
        json.dumps({"raw_file": "sample.jpg", "lanes": [[20, 20, 20], [80, 80, 80]], "h_samples": [20, 50, 70]}),
        encoding="utf-8",
    )

    assert main([str(annotations), "--output-root", str(tmp_path / "processed"), "--split", "train"]) == 0

    assert "Wrote 1 samples" in capsys.readouterr().out
