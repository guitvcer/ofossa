from dataclasses import dataclass, field

from enum import Enum


class BrokerType(Enum):
    kafka = "kafka"
    confluent = "confluent"
    rabbitmq = "rabbitmq"
    nats = "nats"
    redis = "redis"


@dataclass(frozen=True, slots=True)
class Broker:
    typ: BrokerType
    url: str


class Message:
    """Base Message class"""


@dataclass(frozen=True, slots=True)
class RabbitMQMessage(Message):
    name: str
    queue: str
    exchange: str
    body: str
    headers: dict = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KafkaMessage(Message):
    body: str
    topic: str


@dataclass(frozen=True, slots=True)
class NATSMessage(Message):
    body: str
    subject: str


@dataclass(frozen=True, slots=True)
class RedisMessage(Message):
    body: str
    channel: str
