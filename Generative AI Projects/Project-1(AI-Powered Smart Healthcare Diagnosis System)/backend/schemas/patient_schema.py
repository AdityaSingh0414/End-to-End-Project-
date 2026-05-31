from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=0, le=120)
    gender: str = Field(min_length=1, max_length=20)
    glucose_level: float = Field(ge=0, le=500)
    blood_pressure: float = Field(ge=0, le=300)
    cholesterol: float = Field(ge=0, le=500)
    bmi: float = Field(ge=0, le=80)
    symptom_severity: int = Field(ge=1, le=10)
    activity_level: int = Field(ge=1, le=10)
    has_diabetes_history: bool = False
    has_hypertension_history: bool = False
    notes: str = Field(default="")


class PatientCreate(PatientBase):
    pass
