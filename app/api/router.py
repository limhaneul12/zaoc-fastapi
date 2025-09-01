from fastapi import APIRouter

from app.v1.tick import router as tick_router

api = APIRouter()
api.include_router(tick_router, prefix="/v1", tags=["tick"])