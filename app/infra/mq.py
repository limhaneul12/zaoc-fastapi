import orjson
from aiokafka import AIOKafkaProducer
from app.errors import InfraError
import asyncio


class KafkaProducer:
    def __init__(self, bootstrap_servers: str, loop=None) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: orjson.dumps(v),
            loop=loop or asyncio.get_event_loop(),
        )

    async def start(self) -> None:
        try:
            await self._producer.start()
        except Exception as e:
            raise InfraError(f"Kafka producer start failed: {e}")

    async def stop(self):
        await self._producer.stop()

    async def publish(self, topic: str, key: str | None, value: dict):
        try:
            await self._producer.send_and_wait(
                topic, key=key.encode() if key else None, value=value
            )
        except Exception as e:
            raise InfraError(f"Kafka publish failed: {e}")
