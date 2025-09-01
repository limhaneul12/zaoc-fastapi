# app/v1/latest.py
from fastapi import APIRouter
from app.main import price_cache

router = APIRouter()


@router.get("/latest/{symbol}")
async def get_latest(symbol: str):
    if price_cache is None:
        raise RuntimeError("infrastructure not initialized")

    doc = await price_cache.get_latest(symbol)
    if doc is None:
        # 정상 분기 실패 → HTTP 200 + 명시적 found=false
        return {"found": False, "symbol": symbol.upper()}
    # 성공
    return {"found": True, **doc}
