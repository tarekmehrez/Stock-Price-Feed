import json
import aioredis
import asyncio
import pytest


import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app import settings

settings.RUNNING_TESTS = True


def block_on(future):
    return asyncio.get_event_loop().run_until_complete(future)


async def redis_execute(*exec_list):
    conn = await aioredis.create_connection(settings.REDIS_URI, encoding="utf-8")
    await conn.execute(*exec_list)
    conn.close()
    await conn.wait_closed()


@pytest.fixture
def client():
    with TestClient(app) as my_client:
        block_on(redis_execute("FLUSHALL"))
        yield my_client


@pytest.fixture
def mock_function(mocker):
    def mock_function_call(function, return_value, side_effect=None):
        future = asyncio.Future()
        future.set_result(return_value)
        mock = mocker.patch(function, return_value=future, side_effect=side_effect)
        return mock

    return mock_function_call


@pytest.fixture
def seed_instruments():
    instruments = [
        {"description": "graece porta laoreet", "isin": "YA3Q15371402"},
        {
            "description": "dolorum porttitor quaeque verear laoreet",
            "isin": "XK165564K480",
        },
        {
            "description": "nunc persecuti ligula iriure possim sanctus",
            "isin": "UC0M45048835",
        },
        {"description": "eget in inceptos", "isin": "MY41J54K72A6"},
    ]
    for i in instruments:
        block_on(
            redis_execute(
                "SET", f'{settings.INSTRUMENT_PREFIX}:{i["isin"]}', json.dumps(i)
            )
        )


@pytest.fixture
def mock_tsdb_call(mocker):
    # index is a timestamp
    data = {
        "isin": {
            "1618498617819": "AD1308625PG1",
            "1618498618818": "AD1308625PG1",
            "1618498619040": "AD1308625PG1",
            "1618498621146": "AD1308625PG1",
            "1618498624992": "AD1308625PG1",
            "1618498625487": "AD1308625PG1",
        },
        "price": {
            "1618498617819": 726.5652,
            "1618498618818": 746.0,
            "1618498619040": 775.4348,
            "1618498621146": 833.8696,
            "1618498624992": 865.3043,
            "1618498625487": 871.7391,
        },
    }
    df = pd.read_json(json.dumps(data))
    mocker.patch("app.actions.feed.tsdb.read", return_value=df)
