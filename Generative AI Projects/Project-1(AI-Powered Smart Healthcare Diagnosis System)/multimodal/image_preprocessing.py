from pathlib import Path


def preprocess(image_path: str) -> dict[str, object]:
    path = Path(image_path)
    return {"exists": path.exists(), "path": str(path)}
