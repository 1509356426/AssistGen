from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Sequence

import onnx
import torch
from torch import nn

from lane_classification.checkpoint import load_checkpoint
from lane_classification.model import create_resnet18_binary_model
from lane_classification.train import _positive_int


def export_checkpoint_to_onnx(
    checkpoint_path: str | Path,
    output_path: str | Path,
    image_size: int = 224,
    opset: int = 12,
    device: str = "cpu",
    model_factory: Callable[[], nn.Module] = create_resnet18_binary_model,
) -> Path:
    if image_size <= 0:
        raise ValueError("image_size must be positive")
    if opset <= 0:
        raise ValueError("opset must be positive")

    output = Path(output_path)
    if output.is_dir():
        raise IsADirectoryError(f"Output path is a directory: {output}")
    if output.parent:
        output.parent.mkdir(parents=True, exist_ok=True)

    torch_device = torch.device(device)
    model, _, _ = load_checkpoint(
        checkpoint_path,
        device=torch_device,
        model_factory=model_factory,
    )
    model.eval()
    sample_input = torch.randn(1, 3, image_size, image_size, device=torch_device)
    torch.onnx.export(
        model,
        sample_input,
        str(output),
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={
            "input": {0: "batch"},
            "logits": {0: "batch"},
        },
        opset_version=opset,
        dynamo=False,
    )

    exported_model = onnx.load(str(output))
    onnx.checker.check_model(exported_model)
    return output


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a lane classifier checkpoint to ONNX.")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--image-size", type=_positive_int, default=224)
    parser.add_argument("--opset", type=_positive_int, default=12)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.checkpoint.is_file():
        parser.error(f"--checkpoint must be an existing file: {args.checkpoint}")
    if args.output.is_dir():
        parser.error(f"--output must be a file path, not a directory: {args.output}")

    output = export_checkpoint_to_onnx(
        checkpoint_path=args.checkpoint,
        output_path=args.output,
        device=args.device,
        image_size=args.image_size,
        opset=args.opset,
    )
    print(f"exported ONNX model to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
