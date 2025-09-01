from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="rt-pipeline")
    kafka_bootstrap: str = Field(default="kafka1:19092")
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"