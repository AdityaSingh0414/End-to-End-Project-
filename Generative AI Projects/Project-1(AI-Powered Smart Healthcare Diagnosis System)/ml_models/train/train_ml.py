"""Placeholder classical ML training script for the healthcare AI portfolio project."""

from pathlib import Path


def main() -> None:
    output = Path(__file__).resolve().parent.parent / "saved_models" / "random_forest.pkl"
    output.write_text("placeholder random forest artifact", encoding="utf-8")
    print(f"Saved classical ML placeholder to {output}")


if __name__ == "__main__":
    main()
