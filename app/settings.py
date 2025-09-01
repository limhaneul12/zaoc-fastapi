# app/settings.py (추가/갱신)
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="rt-pipeline")
    kafka_bootstrap: str = Field(default="localhost:9092")
    kafka_topic_ticks: str = Field(default="ticks")
    kafka_group_id: str = Field(default="rt-consumer-1")
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_ttl_sec: int = Field(default=300)
    consumer_backoff_ms: int = Field(default=1500)  # 재시도 백오프
    circuit_fail_threshold: int = Field(default=5)  # 연속 실패 n회 시 open

    class Config:
        env_file = ".env"


settings = Settings()
