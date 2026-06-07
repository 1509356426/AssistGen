import torch
from torch import nn
from torchvision.models import ResNet

from lane_classification.model import create_resnet18_binary_model


def test_resnet18_binary_model_has_two_logit_head() -> None:
    model = create_resnet18_binary_model()

    assert isinstance(model, ResNet)
    assert isinstance(model.fc, nn.Linear)
    assert model.fc.out_features == 2


def test_resnet18_binary_model_forward_pass_returns_two_logits() -> None:
    model = create_resnet18_binary_model()
    model.eval()

    with torch.no_grad():
        logits = model(torch.randn(2, 3, 64, 64))

    assert logits.shape == (2, 2)
    assert logits.dtype == torch.float32
