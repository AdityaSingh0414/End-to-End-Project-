from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def search_documents():

    return {
        "message":
        "Search Module Coming Soon"
    }