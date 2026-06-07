from collections.abc import Sequence

from torchvision import transforms


DEFAULT_IMAGE_SIZE = (224, 224)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def _normalize_size(image_size: int | Sequence[int]) -> tuple[int, int]:
    if isinstance(image_size, int):
        return (image_size, image_size)
    if len(image_size) != 2:
        raise ValueError("image_size must be an int or a two-item sequence")
    return (int(image_size[0]), int(image_size[1]))


def get_train_transform(image_size: int | Sequence[int] = DEFAULT_IMAGE_SIZE):
    size = _normalize_size(image_size)
    return transforms.Compose(
        [
            transforms.Resize(size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_eval_transform(image_size: int | Sequence[int] = DEFAULT_IMAGE_SIZE):
    size = _normalize_size(image_size)
    return transforms.Compose(
        [
            transforms.Resize(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )
