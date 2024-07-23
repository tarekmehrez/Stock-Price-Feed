from enum import Enum
from typing import List
from datetime import datetime

from pydantic import BaseModel


class Instrument(BaseModel):
    isin: str
    description: str
    last_price: float = None
    change: float = None
    change_prc: float = None


class InstrumentsPaginate(BaseModel):
    count: int
    results: List[Instrument]


class Quote(BaseModel):
    isin: str
    price: float = None
    index: datetime = None


class CandleStickAggregates(BaseModel):
    high: float
    low: float
    open: float
    close: float
    open_ts: datetime
    close_ts: datetime


class CandleStick(BaseModel):
    timestamp: datetime
    data: CandleStickAggregates


class Feed(BaseModel):
    candle_sticks: List[CandleStick]


class InstrumentWithFeed(Instrument):
    feed: Feed = None
