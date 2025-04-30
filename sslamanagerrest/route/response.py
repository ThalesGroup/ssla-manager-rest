from typing import Optional, Dict, Any

from fastapi import HTTPException


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

        detail = {"message": message, "reason": exception.args}
        super().__init__(status_code=status, detail=detail, headers=headers)
