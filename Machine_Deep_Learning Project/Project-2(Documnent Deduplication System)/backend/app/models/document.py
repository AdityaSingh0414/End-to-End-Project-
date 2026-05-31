from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from app.database.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    filename = Column(String)

    filepath = Column(String)

    file_size = Column(Integer)

    upload_time = Column(
        DateTime,
        default=datetime.utcnow
    )

    status = Column(
        String,
        default="uploaded"
    )