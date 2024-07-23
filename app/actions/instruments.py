import json
from aioredis import Redis

from app.errors import create_404_exception
from app.errors import ErrorTypes
from app.actions import utils
from app.actions import feed
from app.validators import instruments as validators
from app.settings import INSTRUMENT_PREFIX


async def list_instruments(
    page: int, page_size: int, search: str, redis: Redis
) -> validators.InstrumentsPaginate:
    redis_pattern = f"{INSTRUMENT_PREFIX}:{search}*"
    instrument_names = await utils.redis_list(pattern=redis_pattern, redis=redis)

    instrument_pages = [
        instrument_names[i : i + page_size]
        for i in range(0, len(instrument_names), page_size)
    ]
    keys = (
        instrument_pages[page - 1]
        if instrument_names and page <= len(instrument_pages)
        else []
    )
    result = []
    for key in keys:
        instrument_data = await utils.redis_fetch(key, redis)
        instrument = validators.Instrument(**instrument_data)
        instrument.last_price = await feed.instrument_last_price(instrument.isin)
        instrument.change, instrument.change_prc = await feed.instrument_price_change(
            instrument.isin
        )

        result.append(instrument)

    return validators.InstrumentsPaginate(count=len(result), results=result,)


async def fetch_instrument(
    isin: str, minutes: int, redis: Redis
) -> validators.InstrumentWithFeed:
    redis_key = f"{INSTRUMENT_PREFIX}:{isin}"
    instrument_json = await utils.redis_fetch(redis_key, redis)

    if not instrument_json:
        raise create_404_exception(
            code=ErrorTypes.INSTRUMENT_NOT_FOUND, message="Instrument not found",
        )

    instrument = validators.InstrumentWithFeed(**instrument_json)
    instrument.feed = await feed.get_instrument_data(isin, minutes)
    instrument.last_price = await feed.instrument_last_price(isin)
    instrument.change, instrument.change_prc = await feed.instrument_price_change(
        instrument.isin
    )

    return instrument


async def add_instrument(instrument: validators.Instrument, redis: Redis) -> None:
    redis_key = f"{INSTRUMENT_PREFIX}:{instrument.isin}"
    await utils.redis_write(key=redis_key, val=instrument.dict(), redis=redis)


async def delete_instrument(isin: str, redis: Redis) -> None:
    redis_key = f"{INSTRUMENT_PREFIX}:{isin}"
    await utils.redis_delete(key=redis_key, redis=redis)
    await feed.delete_instrument_data(isin)
