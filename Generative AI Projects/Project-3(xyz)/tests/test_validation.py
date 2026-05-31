from pathlib import Path

from ml.preprocessing.validate_data import validate_symptom_dataset


def test_demo_symptom_dataset_validates():
    path = Path("data/raw/symptom_patient_records.csv")
    if path.exists():
        df = validate_symptom_dataset(path)
        assert not df.empty

