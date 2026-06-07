from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import numpy as np
import onnxruntime as ort
from PIL import Image

from lane_classification.checkpoint import DEFAULT_CLASS_NAMES
from lane_classification.train import _positive_int
from lane_classification.transforms import get_eval_transform


def predict_onnx_image(
    model_path: str | Path,
    image_path: str | Path,
    image_size: int = 224,
    providers: Sequence[str] | None = None,
) -> dict:
    if image_size <= 0:
        raise ValueError("image_size must be positive")

    model = Path(model_path)
    if not model.is_file():
        raise FileNotFoundError(f"ONNX model does not exist: {model}")
    image_file = Path(image_path)
    if not image_file.is_file():
        raise FileNotFoundError(f"Image does not exist: {image_file}")

    session = ort.InferenceSession(str(model), providers=list(providers) if providers is not None else None)
    input_name = session.get_inputs()[0].name
    transform = get_eval_transform(image_size)
    with Image.open(image_file) as image:
        tensor = transform(image.convert("RGB")).unsqueeze(0)

    outputs = session.run(None, {input_name: tensor.numpy()})
    probabilities = _softmax(np.asarray(outputs[0], dtype=np.float32))[0]
    index = int(probabilities.argmax())
    return {
        "label": DEFAULT_CLASS_NAMES[index],
        "confidence": float(probabilities[index]),
        "probabilities": {
            class_name: float(probabilities[class_index])
            for class_index, class_name in enumerate(DEFAULT_CLASS_NAMES)
        },
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ONNX Runtime prediction for one lane image.")
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--image-size", type=_positive_int, default=224)
    parser.add_argument("--provider", action="append", dest="providers")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.model.is_file():
        parser.error(f"--model must be an existing file: {args.model}")
    if not args.image.is_file():
        parser.error(f"--image must be an existing file: {args.image}")

    prediction = predict_onnx_image(
        model_path=args.model,
        image_path=args.image,
        image_size=args.image_size,
        providers=args.providers,
    )
    print(json.dumps(prediction, sort_keys=True))
    return 0


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=1, keepdims=True)


if __name__ == "__main__":
    raise SystemExit(main())
