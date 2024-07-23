import json
import datetime

import pandas as pd


from app.actions import feed
from app.tests.conftest import block_on
from app.validators import sockets as message_validators
from app.validators import instruments as instruments_validators


def test_add_tick():
    quote_message = message_validators.QuoteMessage(
        type=message_validators.QuoteTypes.QUOTE,
        data=instruments_validators.Quote(isin="123", price=500.0),
    )
    block_on(feed.add_tick(quote_message))


def test_delete_instrument_data(client, seed_instruments):

    # add som instrument data
    quote_message = message_validators.QuoteMessage(
        type=message_validators.QuoteTypes.QUOTE,
        data=instruments_validators.Quote(isin="YA3Q15371402", price=500.0),
    )
    for _ in range(10):
        block_on(feed.add_tick(quote_message))

    # get instrument, should have last price
    url = "/instruments/YA3Q15371402"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["last_price"] == 500.0

    # delete instrument data
    block_on(feed.delete_instrument_data(isin="YA3Q15371402"))

    # get instrument again, no last price
    url = "/instruments/YA3Q15371402"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()
    assert not response_json["last_price"]


def test_delete_instrument_data_not_exist():
    block_on(feed.delete_instrument_data(isin="someisin"))


def test_make_candle_sticks():
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
    result = block_on(feed.make_candle_sticks_df(df))
    result = result.to_dict(orient="index")

    expected = {
        "2021-04-15 14:56": {
            "high": 775.4348,
            "low": 726.5652,
            "open": 726.5652,
            "close": 775.4348,
            "open_ts": "2021-04-15 16:54:57.819000+02:00",
            "close_ts": "2021-04-15 16:54:59.040000+02:00",
        },
        "2021-04-15 14:57": {
            "high": 871.7391,
            "low": 833.8696,
            "open": 833.8696,
            "close": 871.7391,
            "open_ts": "2021-04-15 14:57:01.146000+02:00",
            "close_ts": "2021-04-15 14:57:05.487000+02:00",
        },
    }
    assert round(result["2021-04-15 14:56"]["high"], 2) == round(
        expected["2021-04-15 14:56"]["high"], 2
    )
    assert round(result["2021-04-15 14:56"]["low"], 2) == round(
        expected["2021-04-15 14:56"]["low"], 2
    )
    assert round(result["2021-04-15 14:56"]["open"], 2) == round(
        expected["2021-04-15 14:56"]["open"], 2
    )
    assert round(result["2021-04-15 14:56"]["close"], 2) == round(
        expected["2021-04-15 14:56"]["close"], 2
    )


def test_make_candle_sticks_empty_df():
    df = pd.DataFrame()
    result = block_on(feed.make_candle_sticks_df(df))
    assert result.empty


def test_get_instrument_data(mock_tsdb_call):
    result = block_on(feed.get_instrument_data(isin="AD1308625PG1", minutes=30))

    expected = {
        "candle_sticks": [
            {
                "timestamp": datetime.datetime(2021, 4, 15, 14, 56),
                "data": {
                    "high": 775.4348,
                    "low": 726.5652,
                    "open": 726.5652,
                    "close": 775.4348,
                    "open_ts": datetime.datetime(2021, 4, 15, 14, 56, 57, 819000),
                    "close_ts": datetime.datetime(2021, 4, 15, 14, 56, 59, 40000),
                },
            },
            {
                "timestamp": datetime.datetime(2021, 4, 15, 14, 57),
                "data": {
                    "high": 871.7391,
                    "low": 833.8696,
                    "open": 833.8696,
                    "close": 871.7391,
                    "open_ts": datetime.datetime(2021, 4, 15, 14, 57, 1, 146000),
                    "close_ts": datetime.datetime(2021, 4, 15, 14, 57, 5, 487000),
                },
            },
        ]
    }

    assert expected == result.dict()


def test_get_instrument_data_empty():
    result = block_on(feed.get_instrument_data(isin="AD1308625PG1", minutes=30))
    expected = {"candle_sticks": []}

    assert expected == result.dict()


def test_get_last_price(mock_tsdb_call):
    result = block_on(feed.instrument_last_price(isin="AD1308625PG1"))
    assert result == 871.74


def test_get_last_price_empty():
    result = block_on(feed.instrument_last_price(isin="AD1308625PG1"))
    assert result == None
