from app.domain.tick import Tick
from app.dto.tick import TickIn


def to_domain(dto: TickIn) -> Tick:
    return Tick(
        symbol=dto.symbol,
        price=dto.price,
        ts_ms=dto.ts_ms,
    )