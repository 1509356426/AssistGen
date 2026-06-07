"""Prepare TuSimple-style lane annotations for binary ROI classification."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image

CLASS_TO_INDEX = {"outside": 0, "inside": 1}
INDEX_TO_CLASS = {value: key for key, value in CLASS_TO_INDEX.items()}
INVALID_X_VALUES = {-2}


@dataclass(frozen=True)
class TusimpleAnnotation:
    raw_file: str
    lanes: list[list[float]]
    h_samples: list[float]


@dataclass(frozen=True)
class ProcessedSample:
    source_path: Path
    output_path: Path
    label: str
    roi: tuple[int, int, int, int]


def parse_tusimple_jsonl(path: str | Path) -> list[TusimpleAnnotation]:
    """Parse TuSimple JSON-lines annotations."""

    annotations: list[TusimpleAnnotation] = []
    jsonl_path = Path(path)
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{jsonl_path}:{line_number}: invalid JSON") from exc

            missing = {"raw_file", "lanes", "h_samples"} - payload.keys()
            if missing:
                fields = ", ".join(sorted(missing))
                raise ValueError(f"{jsonl_path}:{line_number}: missing fields: {fields}")
            if not isinstance(payload["raw_file"], str):
                raise ValueError(f"{jsonl_path}:{line_number}: raw_file must be a string")
            if not isinstance(payload["lanes"], list) or not all(
                isinstance(lane, list) for lane in payload["lanes"]
            ):
                raise ValueError(f"{jsonl_path}:{line_number}: lanes must be a list of lists")
            if not isinstance(payload["h_samples"], list):
                raise ValueError(f"{jsonl_path}:{line_number}: h_samples must be a list")

            h_samples = [_as_number(value, jsonl_path, line_number, "h_samples") for value in payload["h_samples"]]
            lanes: list[list[float]] = []
            for lane_index, lane in enumerate(payload["lanes"]):
                if len(lane) != len(h_samples):
                    raise ValueError(
                        f"{jsonl_path}:{line_number}: lane {lane_index} length does not match h_samples"
                    )
                lanes.append([_as_number(value, jsonl_path, line_number, f"lanes[{lane_index}]") for value in lane])

            annotations.append(
                TusimpleAnnotation(raw_file=payload["raw_file"], lanes=lanes, h_samples=h_samples)
            )

    return annotations


def default_roi(image_size: tuple[int, int]) -> tuple[int, int, int, int]:
    """Return a lower-middle crop bounded to image dimensions."""

    width, height = image_size
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")

    left = min(round(width * 0.25), width - 1)
    right = max(round(width * 0.75), left + 1)
    top = min(round(height * 0.55), height - 1)
    bottom = max(round(height * 0.95), top + 1)
    return bound_roi((left, top, right, bottom), image_size)


def bound_roi(
    roi: Sequence[int | float],
    image_size: tuple[int, int],
) -> tuple[int, int, int, int]:
    width, height = image_size
    if len(roi) != 4:
        raise ValueError("roi must contain left, top, right, bottom")

    left, top, right, bottom = (round(float(value)) for value in roi)
    left = min(max(left, 0), width)
    right = min(max(right, 0), width)
    top = min(max(top, 0), height)
    bottom = min(max(bottom, 0), height)
    if right <= left or bottom <= top:
        raise ValueError(f"roi is empty after bounding: {(left, top, right, bottom)}")
    return left, top, right, bottom


def classify_roi_center(
    annotation: TusimpleAnnotation,
    image_size: tuple[int, int],
    roi: Sequence[int | float] | None = None,
) -> str | None:
    """Classify whether the ROI center lies inside the nearest lane boundaries."""

    bounded_roi = default_roi(image_size) if roi is None else bound_roi(roi, image_size)
    roi_center_x = (bounded_roi[0] + bounded_roi[2]) / 2
    roi_center_y = (bounded_roi[1] + bounded_roi[3]) / 2
    image_center_x = image_size[0] / 2

    lane_x_values = [
        value
        for value in (
            interpolate_lane_x(lane, annotation.h_samples, roi_center_y)
            for lane in annotation.lanes
        )
        if value is not None
    ]
    left_candidates = [value for value in lane_x_values if value < image_center_x]
    right_candidates = [value for value in lane_x_values if value > image_center_x]
    if not left_candidates or not right_candidates:
        return None

    left_boundary = max(left_candidates)
    right_boundary = min(right_candidates)
    return "inside" if left_boundary <= roi_center_x <= right_boundary else "outside"


def find_main_lane_boundaries(
    annotation: TusimpleAnnotation,
    image_size: tuple[int, int],
    target_y: float,
) -> tuple[float, float] | None:
    """Return nearest valid left/right lane boundaries around image center."""

    image_center_x = image_size[0] / 2
    lane_x_values = [
        value
        for value in (
            interpolate_lane_x(lane, annotation.h_samples, target_y)
            for lane in annotation.lanes
        )
        if value is not None
    ]
    left_candidates = [value for value in lane_x_values if value < image_center_x]
    right_candidates = [value for value in lane_x_values if value > image_center_x]
    if not left_candidates or not right_candidates:
        return None

    left_boundary = max(left_candidates)
    right_boundary = min(right_candidates)
    if right_boundary <= left_boundary:
        return None
    return left_boundary, right_boundary


def centered_roi(
    center_x: float,
    center_y: float,
    roi_width: int,
    roi_height: int,
) -> tuple[int, int, int, int]:
    left = round(center_x - roi_width / 2)
    top = round(center_y - roi_height / 2)
    return left, top, left + roi_width, top + roi_height


def roi_within_image(roi: Sequence[int | float], image_size: tuple[int, int]) -> bool:
    if len(roi) != 4:
        raise ValueError("roi must contain left, top, right, bottom")
    left, top, right, bottom = roi
    width, height = image_size
    return 0 <= left < right <= width and 0 <= top < bottom <= height


def dynamic_rois_for_annotation(
    annotation: TusimpleAnnotation,
    image_size: tuple[int, int],
    roi_width: int = 560,
    roi_height: int = 288,
    target_y: float = 540,
    outside_offset_ratio: float = 0.05,
    outside_side: str = "left",
) -> list[tuple[str, str, tuple[int, int, int, int]]]:
    boundaries = find_main_lane_boundaries(annotation, image_size, target_y)
    if boundaries is None:
        return []

    left_boundary, right_boundary = boundaries
    lane_width = right_boundary - left_boundary
    if lane_width <= 0:
        return []

    rois: list[tuple[str, str, tuple[int, int, int, int]]] = []
    lane_center = (left_boundary + right_boundary) / 2
    inside_roi = centered_roi(lane_center, target_y, roi_width, roi_height)
    if (
        roi_within_image(inside_roi, image_size)
        and classify_roi_center(annotation, image_size, inside_roi) == "inside"
    ):
        rois.append(("inside", "inside", inside_roi))

    half_width = roi_width / 2
    margin = max(1, outside_offset_ratio * min(lane_width, roi_width))
    if outside_side in {"left", "both"}:
        center_x = _outside_left_center(left_boundary, margin, half_width)
        if center_x is not None:
            outside_roi = centered_roi(center_x, target_y, roi_width, roi_height)
            if (
                roi_within_image(outside_roi, image_size)
                and classify_roi_center(annotation, image_size, outside_roi) == "outside"
            ):
                rois.append(("outside", "outside_left", outside_roi))
    if outside_side in {"right", "both"}:
        center_x = _outside_right_center(right_boundary, margin, half_width, image_size[0])
        if center_x is not None:
            outside_roi = centered_roi(center_x, target_y, roi_width, roi_height)
            if (
                roi_within_image(outside_roi, image_size)
                and classify_roi_center(annotation, image_size, outside_roi) == "outside"
            ):
                rois.append(("outside", "outside_right", outside_roi))
    return rois


def _outside_left_center(left_boundary: float, margin: float, half_width: float) -> float | None:
    preferred_center = left_boundary - margin
    if preferred_center >= half_width:
        return preferred_center
    if half_width < left_boundary:
        return half_width
    return None


def _outside_right_center(
    right_boundary: float,
    margin: float,
    half_width: float,
    image_width: int,
) -> float | None:
    preferred_center = right_boundary + margin
    rightmost_center = image_width - half_width
    if preferred_center <= rightmost_center:
        return preferred_center
    if rightmost_center > right_boundary:
        return rightmost_center
    return None


def interpolate_lane_x(
    lane: Sequence[int | float],
    h_samples: Sequence[int | float],
    target_y: float,
) -> float | None:
    points = [
        (float(y), float(x))
        for x, y in zip(lane, h_samples, strict=True)
        if _is_valid_lane_x(x)
    ]
    if not points:
        return None
    points.sort()

    if target_y < points[0][0] or target_y > points[-1][0]:
        return None
    for y, x in points:
        if y == target_y:
            return x

    for (y0, x0), (y1, x1) in zip(points, points[1:], strict=False):
        if y0 <= target_y <= y1:
            if y1 == y0:
                return x0
            ratio = (target_y - y0) / (y1 - y0)
            return x0 + ratio * (x1 - x0)
    return None


def prepare_tusimple_dataset(
    annotations_path: str | Path,
    image_root: str | Path | None = None,
    output_root: str | Path = Path("data") / "processed",
    split: str = "train",
    roi: Sequence[int | float] | None = None,
    mode: str = "fixed",
    roi_width: int = 560,
    roi_height: int = 288,
    target_y: float = 540,
    outside_offset_ratio: float = 0.05,
    outside_side: str = "left",
) -> list[ProcessedSample]:
    """Crop and write processed classification samples."""

    if mode not in {"fixed", "dynamic"}:
        raise ValueError("mode must be fixed or dynamic")
    if roi_width <= 0:
        raise ValueError("roi_width must be positive")
    if roi_height <= 0:
        raise ValueError("roi_height must be positive")
    if outside_offset_ratio <= 0:
        raise ValueError("outside_offset_ratio must be positive")
    if outside_side not in {"left", "right", "both"}:
        raise ValueError("outside_side must be left, right, or both")

    annotations_file = Path(annotations_path)
    root = Path(image_root) if image_root is not None else annotations_file.parent
    split_root = Path(output_root) / split
    for class_name in CLASS_TO_INDEX:
        (split_root / class_name).mkdir(parents=True, exist_ok=True)

    processed: list[ProcessedSample] = []
    skipped_by_name: dict[str, int] = {}
    for annotation in parse_tusimple_jsonl(annotations_file):
        source_path = root / annotation.raw_file
        with Image.open(source_path) as image:
            rgb_image = image.convert("RGB")
            stem = Path(annotation.raw_file).stem

            if mode == "fixed":
                bounded_roi = default_roi(rgb_image.size) if roi is None else bound_roi(roi, rgb_image.size)
                label = classify_roi_center(annotation, rgb_image.size, bounded_roi)
                if label is None:
                    continue

                skipped_by_name[stem] = skipped_by_name.get(stem, 0) + 1
                output_name = f"{stem}_{skipped_by_name[stem]:04d}.jpg"
                output_path = split_root / label / output_name
                rgb_image.crop(bounded_roi).save(output_path, format="JPEG")
                processed.append(
                    ProcessedSample(
                        source_path=source_path,
                        output_path=output_path,
                        label=label,
                        roi=bounded_roi,
                    )
                )
                continue

            for label, suffix, dynamic_roi in dynamic_rois_for_annotation(
                annotation=annotation,
                image_size=rgb_image.size,
                roi_width=roi_width,
                roi_height=roi_height,
                target_y=target_y,
                outside_offset_ratio=outside_offset_ratio,
                outside_side=outside_side,
            ):
                count_key = f"{stem}_{suffix}"
                skipped_by_name[count_key] = skipped_by_name.get(count_key, 0) + 1
                output_name = f"{stem}_{skipped_by_name[count_key]:04d}_{suffix}.jpg"
                output_path = split_root / label / output_name
                rgb_image.crop(dynamic_roi).save(output_path, format="JPEG")
                processed.append(
                    ProcessedSample(
                        source_path=source_path,
                        output_path=output_path,
                        label=label,
                        roi=dynamic_roi,
                    )
                )

    return processed


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare TuSimple JSONL annotations for binary classification.")
    parser.add_argument("annotations", type=Path, help="Path to TuSimple-style JSONL annotations.")
    parser.add_argument("--image-root", type=Path, default=None, help="Root directory for raw_file paths.")
    parser.add_argument("--output-root", type=Path, default=Path("data") / "processed")
    parser.add_argument("--split", default="train")
    parser.add_argument("--mode", choices=("fixed", "dynamic"), default="fixed")
    parser.add_argument(
        "--roi",
        nargs=4,
        type=float,
        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
        default=None,
        help="Optional explicit ROI crop.",
    )
    parser.add_argument("--roi-width", type=_positive_int, default=560)
    parser.add_argument("--roi-height", type=_positive_int, default=288)
    parser.add_argument("--target-y", type=float, default=540)
    parser.add_argument("--outside-offset-ratio", type=_positive_float, default=0.05)
    parser.add_argument("--outside-side", choices=("left", "right", "both"), default="left")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    samples = prepare_tusimple_dataset(
        annotations_path=args.annotations,
        image_root=args.image_root,
        output_root=args.output_root,
        split=args.split,
        roi=args.roi,
        mode=args.mode,
        roi_width=args.roi_width,
        roi_height=args.roi_height,
        target_y=args.target_y,
        outside_offset_ratio=args.outside_offset_ratio,
        outside_side=args.outside_side,
    )
    print(f"Wrote {len(samples)} samples to {args.output_root / args.split}")
    return 0


def _as_number(value: object, path: Path, line_number: int, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path}:{line_number}: {field} values must be numeric")
    return float(value)


def _is_valid_lane_x(value: int | float) -> bool:
    return not (float(value) in INVALID_X_VALUES or float(value) < 0)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
