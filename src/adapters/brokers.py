from abc import ABC, abstractmethod
from types import MappingProxyType, TracebackType
from typing import Generic, TypeVar

from faststream.confluent import KafkaBroker as ConfluentBroker
from faststream.kafka import KafkaBroker
from faststream.nats import NatsBroker
from faststream.rabbit import RabbitBroker
from faststream.redis import RedisBroker

from src.domain.entities import (
    Broker,
    BrokerType,
    KafkaMessage,
    Message,
    NATSMessage,
    RabbitMQMessage,
    RedisMessage,
)

_MessageType = TypeVar("_MessageType", bound=Message)


class BrokerAdapter(Generic[_MessageType], ABC):
    @abstractmethod
    def __init__(self, url: str) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> None: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException] | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def publish(self, message: _MessageType) -> None: ...


class _RabbitMQAdapter(BrokerAdapter[RabbitMQMessage]):
    _broker_cls = RabbitBroker

    def __init__(self, url: str) -> None:
        self._url = url
        self._broker = RabbitBroker(url)

    async def __aenter__(self) -> None:
        await self._broker.connect(self._url)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException] | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._broker.close()

    async def publish(self, message: RabbitMQMessage) -> None:
        await self._broker.publish(
            message.body,
            queue=message.queue,
            exchange=message.exchange,
            routing_key=message.name,
            headers=message.headers,
        )


class _KafkaAdapter(BrokerAdapter[KafkaMessage]):
    _broker_cls = KafkaBroker

    def __init__(self, url: str) -> None:
        self._url = url
        self._broker = KafkaBroker(url)

    async def __aenter__(self) -> None:
        await self._broker.connect(self._url)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException] | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._broker.close()

    async def publish(self, message: KafkaMessage) -> None:
        await self._broker.publish(
            message.body,
            message.topic,
        )


class _ConfluentAdapter(BrokerAdapter[KafkaMessage]):
    _broker_cls = ConfluentBroker

    def __init__(self, url: str) -> None:
        self._url = url
        self._broker = ConfluentBroker(url)

    async def __aenter__(self) -> None:
        await self._broker.connect(self._url)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException] | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._broker.close()

    async def publish(self, message: KafkaMessage) -> None:
        await self._broker.publish(
            message.body,
            message.topic,
        )


class _NATSAdapter(BrokerAdapter[NATSMessage]):
    _broker_cls = NatsBroker

    def __init__(self, url: str) -> None:
        self._url = url
        self._broker = NatsBroker(url)

    async def __aenter__(self) -> None:
        await self._broker.connect(self._url)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException] | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._broker.close()

    async def publish(self, message: NATSMessage) -> None:
        await self._broker.publish(
            message.body,
            message.subject,
        )


class _RedisAdapter(BrokerAdapter[RedisMessage]):
    _broker_cls = RedisBroker

    def __init__(self, url: str) -> None:
        self._url = url
        self._broker = RedisBroker(url)

    async def __aenter__(self) -> None:
        await self._broker.connect(self._url)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException] | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._broker.close()

    async def publish(self, message: RedisMessage) -> None:
        await self._broker.publish(
            message.body,
            message.channel,
        )


_BROKER_ADAPTERS_MAP: MappingProxyType[BrokerType, type[BrokerAdapter]] = (
    MappingProxyType(
        {
            BrokerType.rabbitmq: _RabbitMQAdapter,
            BrokerType.kafka: _KafkaAdapter,
            BrokerType.confluent: _ConfluentAdapter,
            BrokerType.nats: _NATSAdapter,
            BrokerType.redis: _RedisAdapter,
        }
    )
)


def create_broker_adapter(
    broker: Broker,
) -> BrokerAdapter:
    broker_adapter_cls = _BROKER_ADAPTERS_MAP.get(broker.typ)
    if broker_adapter_cls:
        return broker_adapter_cls(broker.url)

    raise ValueError("Invalid broker type")
