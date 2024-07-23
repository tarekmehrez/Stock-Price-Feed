from enum import Enum
from fastapi import HTTPException

from fastapi import status
from pydantic import BaseModel


class ErrorTypes(str, Enum):
    INSTRUMENT_NOT_FOUND = "INSTRUMENT_NOT_FOUND"


class ErrorResponse(BaseModel):
    msg: str
    type: ErrorTypes


def create_404_exception(
    code: ErrorTypes, message: str, headers: dict = {}
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorResponse(msg=message, type=code).dict(),
        headers=headers,
    )
