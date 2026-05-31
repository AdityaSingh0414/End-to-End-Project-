from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def rag_chat():

    return {
        "message":
        "RAG Module"
    }