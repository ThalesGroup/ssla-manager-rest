from typing import Optional, Dict, Any, List

from fastapi import HTTPException
from pydantic import BaseModel


def format_exception_chain(exception: BaseException) -> List[str]:
    """
    Flatten an exception and the exceptions it was raised from into readable strings.
    The ssla-manager library chains its exceptions ('raise ... from e'), so the original
    lxml or xsdata message often only lives in the __cause__ of the exception we catch.
    :param exception: the exception to flatten
    :return: one 'ExceptionType: message' entry per exception of the chain, outermost first
    """
    chain: List[str] = []
    seen: set = set()
    current: Optional[BaseException] = exception
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(f"{type(current).__name__}: {current}")
        # __cause__ is set by 'raise ... from e', __context__ by a raise inside an except block
        current = current.__cause__ or current.__context__
    return chain


class ResponseError(HTTPException):
    """
    Response Error class for http libraries.exceptions.
    Allow to precise a custom error message in the http response to provide more information.
    """

    def __init__(self, message: str,
                 exception: Exception,
                 status: int,
                 headers: Optional[Dict[str, Any]] = None, ):
        """
        :param message: A custom message to explain why the error have been raised in the rest api context
        :param exception: The initial exception
        :param status_code: the status code to return to the client
        :param headers: additional headers
        """

        # everything is stringified on purpose: exception args may hold objects that are not
        # JSON serializable, which would turn this error response into a bare 500
        chain = format_exception_chain(exception)
        detail = {"message": message,
                  "error": type(exception).__name__,
                  "reason": str(exception),
                  "causes": chain[1:]}
        super().__init__(status_code=status, detail=detail, headers=headers)


class CreateResponseData(BaseModel):
    status: str
    services: List[str]
