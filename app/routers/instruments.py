import logging

from typing import List
from aioredis import Redis

from fastapi import APIRouter
from fastapi import status
from fastapi import Depends
from fastapi import BackgroundTasks
from fastapi_plugins import depends_redis

from app.providers import RedisConnection
from app.validators.instruments import InstrumentsPaginate
from app.validators.instruments import InstrumentWithFeed
from app.actions import instruments as instruments_actions

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, response_model=InstrumentsPaginate)
async def list_instruments(
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    redis: Redis = Depends(depends_redis),
):
    logging.info(f"Getting all instruments for page {page} with page_size {page_size}")
    result = await instruments_actions.list_instruments(
        page=page, page_size=page_size, search=search, redis=redis
    )
    return result


@router.get(
    "/{isin}", status_code=status.HTTP_200_OK, response_model=InstrumentWithFeed
)
async def fetch_instrument(
    isin: str, minutes: int = 30, redis: Redis = Depends(depends_redis),
):
    logging.info(f"Fetching instrument with isin {isin}")
    result = await instruments_actions.fetch_instrument(
        isin=isin, minutes=minutes, redis=redis
    )
    return result
