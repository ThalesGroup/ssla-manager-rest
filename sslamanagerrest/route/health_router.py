import logging

from fastapi import APIRouter, Response

router = APIRouter()

logger = logging.getLogger("uvicorn.default")


@router.get("",
            summary="service health check",
            response_description="service health",
            responses={
                200: {"description": "service is healthy"}
            })
async def health():
    """
    Take the SSLA in XML format as input and install the proper enablers
    """
    logger.debug("GET /health")
    # return CustomResponse(message="OK", status_code=status.HTTP_200_OK)
    return Response(content="ok")
