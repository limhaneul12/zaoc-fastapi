from fastapi import APIRouter

from app.dto.tick import TickIn
from app.mapping.tick import to_domain
from app.main import producer, price_cache
from app.settings import settings

router = APIRouter()


# app/v1/tick.py (수정 포인트만)
@router.post("/tick", status_code=202)
async def ingest_tick(dto: TickIn):
    tick = to_domain(dto)
    if producer is None:
        raise RuntimeError("Kafka producer not initialized")

    await producer.publish(
        topic=settings.kafka_topic_ticks,
        key=tick.symbol,
        value={"symbol": tick.symbol, "price": tick.price, "ts_ms": tick.ts_ms},
    )
    # 🔽 이전 Step의 임시 캐시 갱신은 제거 (책임 이전)
    return {"ok": True, "symbol": tick.symbol, "price": tick.price, "ts_ms": tick.ts_ms}
