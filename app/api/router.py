from fastapi import APIRouter

from app.v1.tick import router as tick_router
from app.v1.latest import router as latest_router

api = APIRouter()
api.include_router(tick_router, prefix="/v1", tags=["tick"])
api.include_router(latest_router, prefix="/v1", tags=["latest"])
