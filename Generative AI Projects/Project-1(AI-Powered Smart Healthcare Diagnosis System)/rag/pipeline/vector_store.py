import json
from pathlib import Path


def save_vector_store(items: list[dict[str, object]], destination: Path) -> None:
    destination.write_text(json.dumps(items, indent=2), encoding="utf-8")
