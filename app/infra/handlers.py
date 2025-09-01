# app/infra/handlers.py
from __future__ import annotations
from app.infra.cache import PriceCache


def make_on_tick(price_cache: PriceCache):
    async def _handler(payload: dict) -> None:
        # 정상 경로: 최신값 업데이트 (외부 실패시 InfraError 전파)
        await price_cache.set_latest(
            symbol=str(payload["symbol"]),
            price=float(payload["price"]),
            ts_ms=int(payload["ts_ms"]),
        )

    return _handler
