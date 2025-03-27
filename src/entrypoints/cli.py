import asyncio

from typer import prompt, Typer

from src.domain.commands import PublishMessage
from src.domain.entities import (
    Broker,
    BrokerType,
    KafkaMessage,
    Message,
    NATSMessage,
    RabbitMQMessage,
    RedisMessage,
)
from src.service.handlers import handle_command

app = Typer()


@app.command()
def publish(broker_type: BrokerType) -> None:
    broker_url = prompt("URL")
    body = prompt("Message")

    message: Message
    match broker_type:
        case BrokerType.rabbitmq:
            message = _build_rabbitmq_message(body)
        case BrokerType.kafka | BrokerType.confluent:
            message = _build_kafka_message(body)
        case BrokerType.nats:
            message = _build_nats_message(body)
        case BrokerType.redis:
            message = _build_redis_message(body)
        case _:
            raise TypeError("Invalid broker type")

    broker = Broker(broker_type, broker_url)
    command = PublishMessage(broker, message)

    asyncio.run(handle_command(command))

    print("Message published!")  # noqa: WPS421


def _build_rabbitmq_message(body: str) -> RabbitMQMessage:
    routing_key = prompt("Routing Key", default="")
    queue = prompt("Queue", default="")
    exchange = prompt("Exchange", default="")
    headers = prompt("Headers", default="")

    return RabbitMQMessage(routing_key, queue, exchange, body, headers)


def _build_kafka_message(body: str) -> KafkaMessage:
    topic = prompt("Topic")
    return KafkaMessage(topic, body)


def _build_nats_message(body: str) -> NATSMessage:
    subject = prompt("Subject")
    return NATSMessage(subject, body)


def _build_redis_message(body: str) -> RedisMessage:
    channel = prompt("Channel", default="")
    return RedisMessage(channel, body)


if __name__ == "__main__":
    app()
