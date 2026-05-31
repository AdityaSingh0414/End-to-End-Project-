CREATE TABLE IF NOT EXISTS patientrecord (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name VARCHAR(120) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    glucose_level FLOAT NOT NULL,
    blood_pressure FLOAT NOT NULL,
    cholesterol FLOAT NOT NULL,
    bmi FLOAT NOT NULL,
    symptom_severity INTEGER NOT NULL,
    activity_level INTEGER NOT NULL,
    has_diabetes_history BOOLEAN DEFAULT 0,
    has_hypertension_history BOOLEAN DEFAULT 0,
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS predictionrecord (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    model_name VARCHAR(80) NOT NULL,
    recommendations TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patientrecord(id)
);
