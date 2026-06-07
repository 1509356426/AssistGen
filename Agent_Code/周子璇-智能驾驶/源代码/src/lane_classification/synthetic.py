"""Deterministic synthetic TuSimple-style data generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw


def generate_synthetic_tusimple(
    output_root: str | Path,
    split: str = "train",
    count: int = 4,
    image_size: tuple[int, int] = (96, 64),
) -> Path:
    """Generate small deterministic raw images and TuSimple-style annotations."""

    if count <= 0:
        raise ValueError("count must be positive")

    root = Path(output_root)
    image_dir = root / "raw" / split
    image_dir.mkdir(parents=True, exist_ok=True)
    annotations_path = root / f"{split}.jsonl"
    width, height = image_size
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")

    h_samples = list(range(round(height * 0.45), height, max(1, height // 8)))
    with annotations_path.open("w", encoding="utf-8") as handle:
        for index in range(count):
            left_x = round(width * 0.34) + (index % 2)
            right_x = round(width * 0.66) - (index % 2)
            raw_file = f"raw/{split}/sample_{index:04d}.jpg"
            image_path = root / raw_file
            _write_lane_image(image_path, image_size, left_x, right_x, h_samples, index)

            lane_left = [left_x if sample_index % 3 != 0 else -2 for sample_index, _ in enumerate(h_samples)]
            lane_right = [right_x if sample_index % 4 != 0 else -2 for sample_index, _ in enumerate(h_samples)]
            annotation = {
                "raw_file": raw_file,
                "lanes": [lane_left, lane_right],
                "h_samples": h_samples,
            }
            handle.write(json.dumps(annotation, sort_keys=True) + "\n")

    return annotations_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic TuSimple-style data.")
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--split", default="train")
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--height", type=int, default=64)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    annotations_path = generate_synthetic_tusimple(
        output_root=args.output_root,
        split=args.split,
        count=args.count,
        image_size=(args.width, args.height),
    )
    print(f"Wrote annotations to {annotations_path}")
    return 0


def _write_lane_image(
    path: Path,
    image_size: tuple[int, int],
    left_x: int,
    right_x: int,
    h_samples: Sequence[int],
    index: int,
) -> None:
    width, height = image_size
    background = (20 + index * 7 % 25, 24, 32)
    image = Image.new("RGB", image_size, background)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, round(height * 0.55), width, height), fill=(42, 45, 50))
    for x in (left_x, right_x):
        points = [(x, y) for y in h_samples]
        draw.line(points, fill=(240, 240, 210), width=2)
    image.save(path, format="JPEG")


if __name__ == "__main__":
    raise SystemExit(main())
