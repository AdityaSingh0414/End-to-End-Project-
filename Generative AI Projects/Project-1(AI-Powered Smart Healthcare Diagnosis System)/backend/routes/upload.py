from fastapi import APIRouter, File, UploadFile

from backend.services.data_processing import parse_uploaded_csv


router = APIRouter(tags=["Upload"])


@router.post("/upload")
async def upload_patient_file(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    return parse_uploaded_csv(file.filename or "uploaded.csv", content)
