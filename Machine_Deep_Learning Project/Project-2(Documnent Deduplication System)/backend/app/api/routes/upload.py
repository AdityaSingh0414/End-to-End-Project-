import os

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from app.core.config import UPLOAD_DIR

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "size": len(content),
        "message": "Upload Successful"
    }