from enum import Enum
from pydantic import BaseModel

from app.validators.instruments import Instrument
from app.validators.instruments import Quote


class InstrumentOperationTypes(str, Enum):
    ADD = "ADD"
    DELETE = "DELETE"


class QuoteTypes(str, Enum):
    QUOTE = "QUOTE"


class InstrumentMessage(BaseModel):
    type: InstrumentOperationTypes
    data: Instrument


class QuoteMessage(BaseModel):
    type: QuoteTypes
    data: Quote
