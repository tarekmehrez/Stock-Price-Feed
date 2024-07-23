import json
import logging
import asyncio
from typing import Dict

import websockets

from app import settings
from app import providers
from app.validators import sockets as message_validators
from app.actions import instruments as instruments_actions
from app.actions import feed as feed_actions


async def delete_or_add_instrument(
    message: message_validators.InstrumentMessage,
) -> None:
    redis = await providers.RedisConnection.create_connection()

    if message.type == message_validators.InstrumentOperationTypes.ADD:
        logging.info("Adding instrument {message.data.isin}")
        await instruments_actions.add_instrument(message.data, redis)
    elif message.type == message_validators.InstrumentOperationTypes.DELETE:
        logging.info("Deleting instrument {message.data.isin}")
        await instruments_actions.delete_instrument(message.data.isin, redis)


async def consume_instruments() -> None:
    async with websockets.connect(f"{settings.SOCKET_URI}/instruments") as websocket:
        while True:
            message = await websocket.recv()
            instrument_message = message_validators.InstrumentMessage(
                **json.loads(message)
            )
            await delete_or_add_instrument(instrument_message)


async def consume_ticks() -> None:
    async with websockets.connect(f"{settings.SOCKET_URI}/quotes") as websocket:
        while True:
            message = await websocket.recv()
            quote_message = message_validators.QuoteMessage(**json.loads(message))
            await feed_actions.add_tick(quote_message)
