import tempfile
from pathlib import Path

from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from backend.config.settings import settings


def _create_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=False, connect_args=connect_args)


def _temp_database_url() -> str:
    temp_db = Path(tempfile.gettempdir()) / "healthcare_ai.db"
    return f"sqlite:///{temp_db.as_posix()}"


engine = _create_engine(settings.database_url)


def init_db() -> None:
    global engine
    from backend.models.patient_model import PatientRecord
    from backend.models.prediction_model import PredictionRecord

    try:
        SQLModel.metadata.create_all(engine)
    except OperationalError:
        settings.database_url = _temp_database_url()
        engine = _create_engine(settings.database_url)
        SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
