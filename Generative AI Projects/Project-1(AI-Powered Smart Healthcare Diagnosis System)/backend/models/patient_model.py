from typing import Optional

from sqlmodel import Field, SQLModel


class PatientRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_name: str
    age: int
    gender: str
    glucose_level: float
    blood_pressure: float
    cholesterol: float
    bmi: float
    symptom_severity: int
    activity_level: int
    has_diabetes_history: bool = False
    has_hypertension_history: bool = False
    notes: str = ""
