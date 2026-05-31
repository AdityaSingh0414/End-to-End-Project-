from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):

    id: int
    filename: str
    filepath: str
    file_size: int
    upload_time: datetime
    status: str

    class Config:
        from_attributes = True