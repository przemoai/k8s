from fastapi import FastAPI

from src.api.v1.health import health_router

app = FastAPI()

app.include_router(health_router, prefix="/admin")
