import logging

from src.adapters.brokers import create_broker_adapter
from src.domain.commands import Command, PublishMessage

_logger = logging.getLogger(__name__)


async def handle_command(command: Command) -> None:
    if isinstance(command, PublishMessage):
        await _publish_event(command)
    else:
        raise ValueError("Invalid command")


async def _publish_event(command: PublishMessage) -> None:
    _logger.info("Publishing event")

    broker = create_broker_adapter(command.broker)
    async with broker:
        await broker.publish(command.message)

    _logger.info("Published event")
