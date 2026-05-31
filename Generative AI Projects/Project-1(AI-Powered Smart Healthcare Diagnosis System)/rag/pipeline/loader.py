from pathlib import Path


def load_documents(data_dir: Path) -> list[str]:
    return [path.read_text(encoding="utf-8") for path in data_dir.glob("*.txt")]
