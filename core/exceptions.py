from fastapi import HTTPException, status
from .schemas import ErrorDetails
from pydantic import TypeAdapter
from typing import List
from fastapi.encoders import jsonable_encoder


class AppException(HTTPException):
    """
    Exception that allows to handle errors in the code
    The format is the following:
    raise AppException('some string')
    or raise AppException({"type": "some_topic.some_string", "ctx": {"count": 5}})
    the output is always dict:
    {"type": "sometopic_some_string", ...}
    """

    def __init__(self, error):
        error_type = type(error)

        if error_type is str:
            error = {"type": error}

        if error_type is dict and "type" not in error:
            raise Exception("AppException should be string or dict with 'type' key")

        if (error_type not in (list, tuple, )):
            error = [error, ]

        adapter = TypeAdapter(List[ErrorDetails])
        errors = adapter.validate_python(error)

        return super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder(errors))


class DBNotFoundException(Exception):
    pass
