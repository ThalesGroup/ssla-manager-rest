import logging
from http.client import HTTPException
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from lxml.etree import XMLSyntaxError
from sslamanager.parser.ssla_parser import SLO, Metric, ServiceProperties

from sslamanagerrest.environment import get_spm
from sslamanagerrest.route.response import ResponseError, CreateResponseData

router = APIRouter()

logger = logging.getLogger("uvicorn.default")

@router.post("",
             summary="Submit new SSLA",
             response_description="SSLA submission response",
             responses={
                 200: {"description": "SSLA already exists"},
                 201: {"description": "SSLA properly submitted", "model": CreateResponseData},
                 422: {"description": "The SSLA has the wrong format"}
             },
             status_code=status.HTTP_201_CREATED)
async def create_ssla(ssla: "UploadFile" = File(...)):
    """
    Take the SSLA in XML format as input and install the proper enablers
    :param ssla: The SSLA XML file to provide as a form-data.
    :return:
    """
    logger.debug("POST /ssla")
    ssla_content = await ssla.read()
    try:
        ssla = get_spm().create_ssla(ssla_content)
        services_names = ssla.get_services_names()

    except XMLSyntaxError as e:
        return ResponseError(message="unprocessable SSLA content", exception=e,
                             status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    # use 'Exception' instead of custom one because starlette hardly handles custom exceptions
    except Exception as e:
        if "invalid SSLA content" in str(e):
            # ResponseError must be raised and not returned
            raise ResponseError(message="invalid SSLA", exception=e, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif "exist" in str(e):
            return JSONResponse(content="SSLA already exists")
        else:
            raise e

    data = CreateResponseData(status="created", services=services_names)
    return JSONResponse(content=data.model_dump(), status_code=status.HTTP_201_CREATED)


@router.put("",
            summary="Update an existing SSLA",
            response_description="SSLA update response",
            responses={
                200: {"description": "SSLA successfully updated"},
                422: {"description": "The SSLA has the wrong format"}
            },
            status_code=status.HTTP_200_OK)
async def update_ssla(ssla: "UploadFile" = File(...)):
    """
    Take the SSLA in XML format as input and install the proper enablers
    :param ssla: The SSLA XML file to provide as a form-data.
    :return:
    """
    logger.debug("POST /ssla")
    ssla_content = await ssla.read()

    try:
        get_spm().update_ssla(ssla_content)
    except Exception as e:
        if "not found" in str(e):
            return ResponseError(message="SSLA not found to update", exception=e, status=status.HTTP_404_NOT_FOUND)

    return JSONResponse(content="SSLA successfully updated")


@router.get("",
            summary="GET service related list of SSLAs",
            response_description="List of SSLAs related to a service",
            responses={
                200: {"description": "List of SSLA successfully retrieved"},
                404: {"description": "No SSLA found for this service"}
            })
async def get_ssla(service: str):
    logger.debug(f"GET /ssla/{service}")
    try:
        ssla = str(get_spm().get_ssla_content(service))
    except Exception as e:
        if "not found" in str(e):
            return ResponseError(message="Service not found", exception=e, status=status.HTTP_404_NOT_FOUND)
        else:
            raise HTTPException(e)

    return JSONResponse(content=ssla)


@router.delete("/",
               summary="DELETE an SSLA based on its service name",
               response_description="DELETE existing SSLA",
               responses={
                   200: {"description": "SSLA deleted"},
                   404: {"description": "No SSLA found with the provided service name"}
               })
async def delete_ssla(service: str):
    logger.debug(f"DELETE /ssla")
    get_spm().delete_ssla(service)
    return JSONResponse(content="deleted")


@router.get("/services",
            summary="GET services list related to submitted SSLAs",
            response_description="List of services",
            responses={
                200: {"description": "List of services successfully retrieved from submitted SSLAs"},
                404: {"description": "No services found"}
            })
async def get_services():
    logger.debug(f"GET /ssla/services")
    services = get_spm().get_services()
    return JSONResponse(content=services)


@router.get("/slo",
            summary="GET services level objectives of a submitted SSLA",
            response_description="List of SLOs",
            responses={
                200: {"description": "List of SLOs successfully retrieved from submitted SSLAs"},
                404: {"description": "No SLOs found"}
            })
async def get_slos(service: str):
    logger.debug(f"GET /ssla/slo")
    slos = get_spm().get_slos_jsonable(service)
    serialized_slos: List["SLO"] = []
    for slo in slos:
        slo_encoded = jsonable_encoder(slo)
        serialized_slos.append(slo_encoded)
    return JSONResponse(content=serialized_slos)


@router.get("/metrics",
            summary="GET metrics from a submitted SSLA",
            response_description="List of metrics",
            responses={
                200: {"description": "List of metrics successfully retrieved from a submitted SSLA"},
                404: {"description": "No metrics found"}
            })
async def get_metrics(service: str, metric: Optional[str] = None):
    logger.debug(f"GET /ssla/metrics")
    serialized_metrics: List["Metric"] = []
    if metric is not None:
        # optimized request to look for only one metric
        metric = get_spm().get_metric_jsonable(service, metric)
        metric_encoded = jsonable_encoder(metric)
        serialized_metrics.append(metric_encoded)
    else:
        metrics = get_spm().get_metrics_jsonable(service)
        for metric in metrics:
            metric_encoded = jsonable_encoder(metric)
            serialized_metrics.append(metric_encoded)

    return JSONResponse(content=serialized_metrics)


@router.get("/properties",
            summary="GET service properties from a submitted SSLA",
            response_description="List of service properties",
            responses={
                200: {"description": "List of service properties successfully retrieved from a submitted SSLA"},
                404: {"description": "No service properties found"}
            })
async def get_properties(service: str):
    logger.debug(f"GET /ssla/properties")
    properties = get_spm().get_service_properties_jsonable(service)
    serialized_properties: List["ServiceProperties"] = []
    for prop in properties:
        prop_encoded = jsonable_encoder(prop)
        serialized_properties.append(prop_encoded)
    return JSONResponse(content=serialized_properties)
