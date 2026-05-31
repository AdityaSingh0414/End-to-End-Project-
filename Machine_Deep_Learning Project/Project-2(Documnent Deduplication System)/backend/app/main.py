from fastapi import FastAPI

from app.api.routes.upload import router as upload_router
from app.api.routes.search import router as search_router
from app.api.routes.dedup import router as dedup_router
from app.api.routes.cluster import router as cluster_router
from app.api.routes.rag import router as rag_router
from app.api.routes.analytics import router as analytics_router

app = FastAPI(
    title="Document Deduplication Platform"
)

app.include_router(
    upload_router,
    prefix="/documents",
    tags=["Upload"]
)

app.include_router(
    search_router,
    prefix="/search",
    tags=["Search"]
)

app.include_router(
    dedup_router,
    prefix="/dedup",
    tags=["Deduplication"]
)

app.include_router(
    cluster_router,
    prefix="/cluster",
    tags=["Cluster"]
)

app.include_router(
    rag_router,
    prefix="/rag",
    tags=["RAG"]
)

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)


@app.get("/")
def root():
    return {
        "message":
        "Intelligent Document Deduplication Platform Running"
    }