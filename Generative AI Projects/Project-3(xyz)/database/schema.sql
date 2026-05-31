CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    age INT NOT NULL CHECK (age BETWEEN 0 AND 120),
    gender VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clinical_visits (
    visit_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    visit_date DATE NOT NULL,
    temperature_c NUMERIC(4, 1),
    heart_rate INT,
    spo2 INT CHECK (spo2 BETWEEN 50 AND 100),
    risk_level VARCHAR(20),
    disease_label VARCHAR(80)
);

CREATE TABLE symptom_observations (
    observation_id SERIAL PRIMARY KEY,
    visit_id INT REFERENCES clinical_visits(visit_id),
    fever BOOLEAN NOT NULL,
    cough BOOLEAN NOT NULL,
    fatigue BOOLEAN NOT NULL,
    shortness_of_breath BOOLEAN NOT NULL,
    chest_pain BOOLEAN NOT NULL,
    headache BOOLEAN NOT NULL,
    nausea BOOLEAN NOT NULL,
    sore_throat BOOLEAN NOT NULL,
    body_ache BOOLEAN NOT NULL,
    runny_nose BOOLEAN NOT NULL
);

CREATE TABLE imaging_studies (
    study_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    image_path TEXT NOT NULL,
    predicted_label VARCHAR(80),
    confidence NUMERIC(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_decisions (
    decision_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    ml_prediction VARCHAR(80),
    ml_confidence NUMERIC(5, 4),
    dl_prediction VARCHAR(80),
    dl_confidence NUMERIC(5, 4),
    final_decision VARCHAR(80),
    final_score NUMERIC(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

