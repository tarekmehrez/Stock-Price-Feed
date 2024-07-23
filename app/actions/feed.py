import logging
import pytz
from datetime import datetime
from datetime import timedelta

import pandas as pd
from arctic.date import DateRange
from arctic.exceptions import NoDataFoundException

from app.providers import tsdb
from app.validators import instruments as instruments_validators
from app.validators import sockets as message_validators


async def add_tick(quote_message: message_validators.QuoteMessage) -> None:
    quote_message.data.index = datetime.now(tz=pytz.utc)
    tsdb.write(
        symbol=f"FEED::{quote_message.data.isin}", data=[quote_message.data.dict()]
    )


async def delete_instrument_data(isin: str) -> None:
    tsdb.delete(f"FEED::{isin}")


async def make_candle_sticks_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df["timestamp"] = df.index

    min_index = df.index.to_period("min")
    agg_df = df.groupby(min_index)

    high_df = agg_df.price.max().to_frame("high")
    low_df = agg_df.price.min().to_frame("low")
    first_df = agg_df.price.first().to_frame("open")
    close_df = agg_df.price.last().to_frame("close")

    open_ts_df = agg_df.timestamp.first().to_frame("open_ts")
    close_ts_df = agg_df.timestamp.last().to_frame("close_ts")

    dfs = [high_df, low_df, first_df, close_df, open_ts_df, close_ts_df]
    result_df = pd.concat(dfs, axis=1)
    result_df.index = result_df.index.astype(str)
    result_df.open_ts = result_df.open_ts.astype(str)
    result_df.close_ts = result_df.close_ts.astype(str)

    return result_df


async def get_instrument_data(isin: str, minutes: int) -> instruments_validators.Feed:
    now = datetime.now(tz=pytz.utc)
    start = now - timedelta(minutes=minutes)
    try:
        prices_df = tsdb.read(
            f"FEED::{isin}", date_range=DateRange(start=start, end=now)
        )
    except NoDataFoundException:
        logging.info(f"No feed data found for isin {isin}")
        return instruments_validators.Feed(candle_sticks=[])

    candle_sticks_df = await make_candle_sticks_df(prices_df)
    candle_sticks_data = candle_sticks_df.to_dict(orient="index")

    response_data = []
    for key, val in candle_sticks_data.items():
        response_data.append(
            instruments_validators.CandleStick(timestamp=key, data=val)
        )
    return instruments_validators.Feed(candle_sticks=response_data)


async def instrument_last_price(isin: str) -> float:
    now = datetime.now(tz=pytz.utc)
    start = now - timedelta(minutes=1)
    try:
        df = tsdb.read(f"FEED::{isin}", date_range=DateRange(start=start, end=now))
        return round(df.sort_index().price[-1], 2)
    except NoDataFoundException:
        logging.info(f"no last price found for isin {isin}")
        return None


async def instrument_price_change(isin: str) -> (float, float):
    now = datetime.now(tz=pytz.utc)
    start = now - timedelta(minutes=5)
    try:
        df = tsdb.read(f"FEED::{isin}", date_range=DateRange(start=start, end=now))
        last_price = df.sort_index().price[-1]
        first_price = df.sort_index().price[0]
        diff = last_price - first_price
        return (round(diff / first_price, 2), round(diff / first_price * 100, 2))
    except NoDataFoundException:
        logging.info(f"no last price found for isin {isin}")
        return None, None
