# app/main.py (변경)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, JSONResponse

from app.api.router import api
from app.middleware.request_id import RequestIDMiddleware
from app.errors import DomainError, InfraError
from app.infra.mq import KafkaProducer
from app.infra.cache import PriceCache
from app.infra.mq_consumer import ConsumerService
from app.infra.handlers import make_on_tick
from app.settings import settings
from app.domain.consumer_state import ConsumerState

producer: KafkaProducer | None = None
price_cache: PriceCache | None = None
consumer: ConsumerService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer, price_cache, consumer
    # 리소스 준비
    producer = KafkaProducer(bootstrap_servers=settings.kafka_bootstrap)
    price_cache = PriceCache(url=settings.redis_url)
    await producer.start()

    # consumer 시작
    consumer = ConsumerService(
        bootstrap=settings.kafka_bootstrap,
        topic=settings.kafka_topic_ticks,
        group_id=settings.kafka_group_id,
        on_tick=make_on_tick(price_cache),
    )
    await consumer.start()

    try:
        yield
    finally:
        # 종료 순서: consumer -> producer -> redis
        await consumer.stop()
        await producer.stop()
        await price_cache.close()


app = FastAPI(
    title="rt-pipeline",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.include_router(api)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, e: DomainError):
    return JSONResponse({"error": "domain_error", "detail": str(e)}, status_code=400)


@app.exception_handler(InfraError)
async def infra_error_handler(_: Request, e: InfraError):
    return JSONResponse({"error": "infra_error", "detail": str(e)}, status_code=502)


# 상태 노출 (간단 버전)
@app.get("/v1/status")
async def status():
    st = consumer.state.value if consumer else "UNKNOWN"
    return {
        "consumer_state": st,
        "circuit_open": getattr(consumer, "_circuit_open", False) if consumer else None,
        "fail_count": getattr(consumer, "_fail_count", 0) if consumer else None,
        "topic": settings.kafka_topic_ticks,
        "group_id": settings.kafka_group_id,
    }
