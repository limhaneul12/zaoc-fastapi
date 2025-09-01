from fastapi import APIRouter

from app.dto.tick import TickIn
from app.mapping.tick import to_domain

router = APIRouter()

async def ingest_tick(dto: TickIn):
    tick = to_domain(dto)
    
    return {"ok": True, "symbol": tick.symbol, "price": tick.price, "ts_ms": tick.ts_ms}
