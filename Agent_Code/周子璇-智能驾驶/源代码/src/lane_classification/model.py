from torch import nn
from torchvision import models


def create_resnet18_binary_model(weights=None) -> nn.Module:
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, 2)
    return model
