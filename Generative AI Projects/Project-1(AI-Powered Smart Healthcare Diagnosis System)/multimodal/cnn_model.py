"""Placeholder multimodal model definition for future imaging workflows."""


class CNNModel:
    def predict(self, image_path: str) -> dict[str, object]:
        return {"image_path": image_path, "finding": "No acute issue detected", "confidence": 0.77}
