from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tick:
    symbol: str
    price: float
    ts_ms: int
    
    
    