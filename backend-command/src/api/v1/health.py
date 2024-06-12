from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
def health():
    return {"status": "OK"}
