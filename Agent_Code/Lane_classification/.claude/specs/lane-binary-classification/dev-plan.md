# Lane Binary Classification - Development Plan

## Overview
Implement the stage-1 core runnable loop for a greenfield Python lane inside/outside binary classification pipeline, from TuSimple-style preparation through dataset loading, ResNet18 training, evaluation, inference, and synthetic end-to-end verification.

## Task Breakdown

### Task 1: Create Project Skeleton and Dependency Declaration
- **ID**: task-1
- **type**: default
- **Description**: Create the initial Python package layout, declare runtime and test dependencies, and add minimal package/module placeholders needed by later tasks.
- **File Scope**: `requirements.txt`, `src/lane_classification/__init__.py`, package module placeholders as needed.
- **Dependencies**: None
- **Test Command**: `python -m pytest` after tests exist
- **Test Focus**: Package imports succeed, dependency declaration includes required Python ML/test tooling, and the source layout is discoverable by pytest/imports.

### Task 2: Implement TuSimple Preparation and Synthetic Data Generation
- **ID**: task-2
- **type**: default
- **Description**: Implement TuSimple-style JSON-lines annotation parsing, lane ROI/sample extraction, inside/outside label assignment, processed classification directory writing, and a synthetic small dataset/sample generator for local verification without real TuSimple data.
- **File Scope**: `src/lane_classification/prepare_tusimple.py`, `src/lane_classification/synthetic.py`, related utilities, tests under `tests/`.
- **Dependencies**: depends on task-1
- **Test Command**: `python -m pytest tests/test_prepare_tusimple.py tests/test_synthetic.py --cov=src --cov-report=term-missing`
- **Test Focus**: Valid JSON-line annotations are parsed, malformed or missing fields fail clearly, generated inside/outside samples have deterministic labels and expected directory layout, image crops/ROIs are bounded, and synthetic data is reproducible and usable by downstream tasks.

### Task 3: Implement Dataset Loader, Transforms, and Model Factory
- **ID**: task-3
- **type**: default
- **Description**: Implement loading of processed classification directories, image/label transforms, and a ResNet18-based binary classifier factory suitable for training and inference.
- **File Scope**: `src/lane_classification/dataset.py`, `src/lane_classification/transforms.py`, `src/lane_classification/model.py`, tests.
- **Dependencies**: depends on task-1; can run parallel with task-2 if dataset contract is agreed
- **Test Command**: `python -m pytest tests/test_dataset.py tests/test_model.py --cov=src --cov-report=term-missing`
- **Test Focus**: Dataset discovers class directories consistently, returns tensors and integer binary labels, handles empty/missing directories with clear errors, transforms produce expected shapes/dtypes, and the ResNet18 factory returns a two-class/binary output head with forward pass compatibility.

### Task 4: Implement Training, Evaluation, and Single-Image Inference CLIs
- **ID**: task-4
- **type**: default
- **Description**: Implement shared core functions and command-line entry points for training, checkpoint saving/loading, evaluation metrics, and single-image prediction using the processed dataset and ResNet18 binary model.
- **File Scope**: `src/lane_classification/train.py`, `src/lane_classification/evaluate.py`, `src/lane_classification/infer.py`, metrics/checkpoint utilities, tests.
- **Dependencies**: depends on task-2 and task-3
- **Test Command**: `python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=90`
- **Test Focus**: Training runs a smoke epoch on a small dataset, checkpoints are written and reloadable, evaluation reports deterministic binary metrics, inference returns a label/probability for one image, CLI argument validation is clear, and shared code paths are covered by tests.

### Task 5: Add End-to-End Synthetic Pipeline Coverage
- **ID**: task-5
- **type**: default
- **Description**: Add pytest coverage that verifies the full stage-1 loop with synthetic data: generate/prepare samples, train a smoke model, evaluate it, and run single-image inference.
- **File Scope**: `tests/test_end_to_end.py`, possible small test fixtures.
- **Dependencies**: depends on task-2, task-3, and task-4
- **Test Command**: `python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=90`
- **Test Focus**: The synthetic pipeline runs end to end in a temporary directory, generated data can be prepared into the processed classification contract, training produces a checkpoint, evaluation consumes the checkpoint and reports metrics, inference produces a valid binary prediction, and total coverage remains at least 90%.

## Acceptance Criteria
- [ ] Project structure and Python dependencies are declared for the stage-1 greenfield Python package.
- [ ] TuSimple-style JSON-line annotations can be converted into processed inside/outside classification samples.
- [ ] Processed classification directories can be loaded as train/evaluation datasets with deterministic labels and transforms.
- [ ] A ResNet18-based binary classification model can be constructed and used for forward passes.
- [ ] Training CLI can run a smoke training loop and save a reloadable checkpoint.
- [ ] Evaluation CLI can load a checkpoint and report binary classification metrics.
- [ ] Single-image inference CLI can load a checkpoint and return a valid inside/outside prediction.
- [ ] Synthetic sample generation supports local end-to-end verification when real TuSimple data is unavailable.
- [ ] End-to-end pytest coverage verifies prepare -> train smoke -> evaluate -> infer.
- [ ] All unit tests pass.
- [ ] Code coverage ≥90%.

## Technical Notes
- Keep stage-1 limited to the core runnable loop; do not add UI, serving APIs, experiment tracking, or advanced training features.
- Use a `src/lane_classification/` package layout with CLI modules implemented as importable functions plus `if __name__ == "__main__"` entry points where appropriate.
- Prefer deterministic defaults for tests and synthetic data so smoke training and metrics are stable in CI/local runs.
- Keep the processed dataset contract simple and documented in tests, for example class-separated directories for `inside` and `outside` samples.
- Use torchvision ResNet18 with its classification head adapted for binary classification, avoiding pretrained weight downloads during tests unless explicitly configured.
- Tests should use temporary directories and tiny synthetic images to avoid requiring real TuSimple data or large artifacts.
