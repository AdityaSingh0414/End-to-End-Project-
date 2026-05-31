from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def cluster_documents():

    return {
        "message":
        "Clustering Module"
    }