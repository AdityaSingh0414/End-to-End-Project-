from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image


def placeholder_grad_cam(image_path: str | Path, output_path: str | Path) -> None:
    """Create a lightweight heatmap overlay placeholder for portfolio demos."""
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    heat = np.zeros((224, 224, 3), dtype=np.uint8)
    yy, xx = np.mgrid[0:224, 0:224]
    mask = np.exp(-(((xx - 112) ** 2 + (yy - 128) ** 2) / (2 * 38**2)))
    heat[..., 0] = (mask * 255).astype(np.uint8)
    blended = Image.blend(img, Image.fromarray(heat), alpha=0.35)
    blended.save(output_path)


def explain_prediction(model: torch.nn.Module, image_tensor: torch.Tensor) -> torch.Tensor:
    """Hook real Grad-CAM logic here after the DL model is trained on real X-rays."""
    model.eval()
    with torch.no_grad():
        return torch.softmax(model(image_tensor), dim=1)

