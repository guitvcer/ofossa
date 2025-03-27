from dataclasses import dataclass

from src.domain.entities import Broker, Message


class Command:
    """Base Command class"""


@dataclass(frozen=True, slots=True)
class PublishMessage(Command):
    broker: Broker
    message: Message
