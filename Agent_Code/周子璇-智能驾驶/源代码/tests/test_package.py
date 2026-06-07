from pathlib import Path

import lane_classification


def test_package_imports() -> None:
    assert lane_classification.__version__


def test_required_dependencies_are_declared() -> None:
    requirements = {
        line.strip().split("==", maxsplit=1)[0].split(">=", maxsplit=1)[0]
        for line in Path("requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }

    assert {
        "torch",
        "torchvision",
        "Pillow",
        "opencv-python",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "pytest",
        "pytest-cov",
    }.issubset(requirements)
