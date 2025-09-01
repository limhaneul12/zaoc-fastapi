# app/infra/redis.py
from __future__ import annotations
import orjson
import redis.asyncio as redis
from app.errors import InfraError
from app.settings import settings


def _key(symbol: str) -> str:
    return f"latest:{symbol.upper()}"


class PriceCache:
    """심볼별 최신 가격 1건 저장/조회"""

    def __init__(self, url: str):
        self._client = redis.from_url(url, encoding="utf-8", decode_responses=False)
        self._ttl = settings.redis_ttl_sec

    async def set_latest(self, symbol: str, price: float, ts_ms: int) -> None:
        try:
            payload = orjson.dumps({"symbol": symbol, "price": price, "ts_ms": ts_ms})
            # SETEX와 동일: SET + EXPIRE
            await self._client.set(_key(symbol), payload, ex=self._ttl)
        except Exception as e:
            raise InfraError(f"redis set failed: {e}")

    async def get_latest(self, symbol: str) -> dict | None:
        try:
            raw = await self._client.get(_key(symbol))
            if raw is None:
                return None
            return orjson.loads(raw)
        except Exception as e:
            raise InfraError(f"redis get failed: {e}")

    async def close(self):
        await self._client.aclose()
