# app/infra/consumer.py
from __future__ import annotations
import asyncio, orjson, logging
from typing import Callable, Awaitable
from aiokafka import AIOKafkaConsumer
from app.domain.consumer_state import ConsumerState
from app.errors import InfraError
from app.settings import settings

log = logging.getLogger(__name__)


class ConsumerService:
    """
    Kafka consumer + 상태머신 + Redis 업데이트.
    """

    def __init__(
        self,
        bootstrap: str,
        topic: str,
        group_id: str,
        on_tick: Callable[[dict], Awaitable[None]],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._bootstrap = bootstrap
        self._topic = topic
        self._group_id = group_id
        self._on_tick = on_tick
        self._loop = loop or asyncio.get_event_loop()

        self._consumer: AIOKafkaConsumer | None = None
        self.state: ConsumerState = ConsumerState.DISCONNECTED
        self._task: asyncio.Task | None = None
        self._stop_evt = asyncio.Event()
        self._fail_count = 0
        self._circuit_open = False

    async def start(self) -> None:
        self.state = ConsumerState.CONNECTING
        try:
            self._consumer = AIOKafkaConsumer(
                self._topic,
                bootstrap_servers=self._bootstrap,
                group_id=self._group_id,
                enable_auto_commit=True,
                value_deserializer=lambda b: orjson.loads(b),
                loop=self._loop,
            )
            await self._consumer.start()
            self._stop_evt.clear()
            self._task = asyncio.create_task(self._run())
            log.info("consumer started")
        except Exception as e:
            self.state = ConsumerState.FAILED
            raise InfraError(f"consumer start failed: {e}")

    async def stop(self) -> None:
        self.state = ConsumerState.STOPPED
        self._stop_evt.set()
        if self._task:
            await asyncio.wait([self._task], timeout=5)
        if self._consumer:
            await self._consumer.stop()
        log.info("consumer stopped")

    async def _run(self) -> None:
        while not self._stop_evt.is_set():
            if self._circuit_open:
                self.state = ConsumerState.RETRYING
                await asyncio.sleep(settings.consumer_backoff_ms / 1000)
                self._circuit_open = False  # 반개방(half-open) 시도

            try:
                assert self._consumer is not None
                self.state = ConsumerState.PROCESSING
                msg = await self._consumer.getone()  # backpressure-friendly
                payload = msg.value  # dict (orjson.loads)
                # 간단 스키마 검사(핵심 필드만, 비용 최소화)
                if (
                    not isinstance(payload, dict)
                    or "symbol" not in payload
                    or "price" not in payload
                    or "ts_ms" not in payload
                ):
                    # 정상 분기 실패 → drop (로그 샘플링)
                    if msg.offset % 100 == 0:
                        log.warning("drop malformed payload at offset=%s", msg.offset)
                    continue

                await self._on_tick(payload)
                self._fail_count = 0  # 성공 시 실패 카운터 리셋

            except Exception as e:
                self.state = ConsumerState.FAILED
                self._fail_count += 1
                log.error("consumer loop error (%s fails): %s", self._fail_count, e)
                if self._fail_count >= settings.circuit_fail_threshold:
                    self._circuit_open = True
                    log.error("circuit opened (fail threshold reached)")
                await asyncio.sleep(settings.consumer_backoff_ms / 1000)
