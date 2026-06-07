# Lane Binary Classification Bonus Features - Development Plan

## Overview
Add optional TensorBoard training telemetry plus ONNX export and ONNX Runtime single-image inference for the completed lane binary classification pipeline.

## Task Breakdown

### Task 1: TensorBoard and Validation Metrics
- **ID**: task-1
- **type**: default
- **Description**: Add optional validation loader support, compute train/validation loss and accuracy, log metrics with `SummaryWriter` when requested, and expose CLI flags `--val-dir` and `--log-dir` while preserving backward-compatible training behavior with no default logging side effects.
- **File Scope**: `src/lane_classification/train.py`, `requirements.txt`, `tests/test_train_evaluate_infer.py`
- **Dependencies**: None
- **Test Command**: `python -m pytest tests/test_train_evaluate_infer.py --cov=src --cov-report=term-missing`
- **Test Focus**: Training still works without validation/logging flags; validation metrics are computed when `--val-dir` is provided; TensorBoard event files are created only when `--log-dir` is provided; train and validation loss/accuracy scalar tags are logged.

### Task 2: ONNX Checkpoint Export
- **ID**: task-2
- **type**: default
- **Description**: Implement reusable ONNX export from a saved PyTorch checkpoint to a `.onnx` file, validate the exported graph with `onnx.checker`, and expose the export path through a CLI entry point.
- **File Scope**: `src/lane_classification/export_onnx.py`, `requirements.txt`, `tests/test_onnx.py`
- **Dependencies**: depends on task-1
- **Test Command**: `python -m pytest tests/test_onnx.py --cov=src --cov-report=term-missing`
- **Test Focus**: Checkpoint loads successfully; ONNX file is written to the requested path; exported graph passes `onnx.checker.check_model`; reusable export function and CLI handle valid arguments and fail clearly for invalid checkpoint/output inputs.

### Task 3: ONNX Runtime Single-Image Inference
- **ID**: task-3
- **type**: default
- **Description**: Implement single-image inference using `onnxruntime.InferenceSession`, reuse the existing evaluation preprocessing transform, return label, confidence, and class probabilities, and expose the functionality through a CLI.
- **File Scope**: `src/lane_classification/infer_onnx.py`, `tests/test_onnx.py`
- **Dependencies**: depends on task-2
- **Test Command**: `python -m pytest tests/test_onnx.py --cov=src --cov-report=term-missing`
- **Test Focus**: ONNX Runtime session loads the exported model; one synthetic image is preprocessed with the expected eval transform; prediction result includes label, confidence, and probabilities; probabilities are valid and confidence matches the selected label; CLI emits parseable inference output.

### Task 4: End-to-End Bonus Validation and Coverage Gate
- **ID**: task-4
- **type**: default
- **Description**: Extend synthetic end-to-end smoke coverage to exercise TensorBoard log creation, ONNX checkpoint export, ONNX Runtime prediction, and the full project coverage gate for all bonus features.
- **File Scope**: `tests/test_end_to_end.py`, `tests/test_onnx.py`
- **Dependencies**: depends on task-1, task-2, task-3
- **Test Command**: `python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=90`
- **Test Focus**: Synthetic training can create TensorBoard logs; a saved checkpoint can be exported to ONNX; exported ONNX model can run single-image inference through ONNX Runtime; total test suite remains at or above 90% coverage.

## Acceptance Criteria
- [ ] TensorBoard logging records train loss, train accuracy, validation loss, and validation accuracy when `--log-dir` is provided.
- [ ] Training remains backward compatible when `--val-dir` and `--log-dir` are omitted, with no default TensorBoard side effects.
- [ ] Saved PyTorch checkpoints can be exported to valid `.onnx` files through both reusable Python API and CLI.
- [ ] ONNX Runtime single-image inference returns label, confidence, and probabilities through both reusable Python API and CLI.
- [ ] No report or PPT generation is added in this bonus stage.
- [ ] All unit and end-to-end tests pass.
- [ ] Code coverage ≥90%.

## Technical Notes
- Treat TensorBoard logging as opt-in only; add `tensorboard` to `requirements.txt` only if it is not already present.
- Add `onnx` and `onnxruntime` to `requirements.txt` only as needed for export and inference tests.
- Reuse existing model construction, checkpoint loading conventions, class-label mapping, and evaluation image transform to avoid divergence between PyTorch and ONNX inference paths.
- Keep ONNX export and inference modules small, reusable, and CLI-friendly; implementation should avoid report/PPT generation or unrelated pipeline changes.
