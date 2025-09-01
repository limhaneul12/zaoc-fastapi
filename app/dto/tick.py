from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr


class TickIn(BaseModel):
    model_config = ConfigDict(extra="ignore") 
    symbol: StrictStr = Field(min_length=1, max_length=16)
    price: StrictFloat = Field(gt=0)
    ts_ms: StrictInt = Field(ge=1_600_000_000_000)  # 예: 합리적 하한