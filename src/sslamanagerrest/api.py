"""
Orchestrator API
Manage the different core.api.routers of the REST API in this file
"""
import logging

from fastapi import APIRouter

from sslamanagerrest.route import ssla_router, health_router

VERSION = 'v1'
DESCRIPTION = {
    "version": VERSION,
    "chart_name": "ssla manager rest api"
}
API_ROUTER_PREFIX = f"/api/{VERSION}"
SSLA_ROUTER_PREFIX = "/ssla"
HEALTH_ROUTER_PREFIX = "/health"

router = APIRouter(prefix=API_ROUTER_PREFIX)

logger = logging.getLogger("uvicorn.default")


def add_route(api_router: APIRouter, prefix: str):
    router.include_router(api_router, prefix=prefix, tags=[prefix.replace("/", "")])


add_route(ssla_router.router, SSLA_ROUTER_PREFIX)
add_route(health_router.router, HEALTH_ROUTER_PREFIX)


@router.get('/')
async def root():
    """
    Return the rest api description in response
    :return: JSON description of the sslaorchestrator rest api
    """
    return {"description": DESCRIPTION}
