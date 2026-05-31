from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def deduplicate():

    return {
        "message":
        "Duplicate Detection Phase"
    }