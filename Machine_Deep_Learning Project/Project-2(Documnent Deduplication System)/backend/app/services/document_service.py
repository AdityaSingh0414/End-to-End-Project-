import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


def save_document(
    file: UploadFile,
    db: Session
):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    content = file.file.read()

    with open(
        file_path,
        "wb"
    ) as buffer:
        buffer.write(content)

    document = Document(
        filename=file.filename,
        filepath=file_path,
        file_size=len(content)
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return document