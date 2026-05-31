from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def analytics():

    return {
        "message":
        "Analytics Dashboard"
    }