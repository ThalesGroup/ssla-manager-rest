import logging
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sslamanager.exceptions import SSLAAlreadyExistsException, SSLAException, SSLAFormatException, \
    SSLAMetricsException, SSLANotFound, SSLAValidationException
from sslamanager.parser.ssla_parser import SLO, Metric, ServiceProperties

from sslamanagerrest.environment import get_spm
from sslamanagerrest.route.response import ResponseError, CreateResponseData

router = APIRouter()

logger = logging.getLogger(__name__)


def ssla_not_found(service: str, exception: Exception) -> "ResponseError":
    """
    Build the 404 error raised when no SSLA is stored for the requested service
    """
    logger.warning(f"no SSLA stored for service '{service}': {exception}")
    return ResponseError(message=f"no SSLA found for service '{service}'", exception=exception,
                         status=status.HTTP_404_NOT_FOUND)

@router.post("",
             summary="Submit new SSLA",
             response_description="SSLA submission response",
             responses={
                 200: {"description": "SSLA already exists", "model": CreateResponseData},
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
        ssla_model = get_spm().create_ssla(ssla_content)
        services_names = ssla_model.get_services_names()

    except SSLAAlreadyExistsException as e:
        logger.info(f"SSLA already submitted: {e}")
        ssla_model = get_spm().ssla_parser.parse_from_content(ssla_content)
        data = CreateResponseData(status="already exists", services=ssla_model.get_services_names())
        return JSONResponse(content=data.model_dump(), status_code=status.HTTP_200_OK)

    # the SSLA content is rejected by the builtin XML schemas of the ssla-manager dependency
    # ResponseError must be raised and not returned, otherwise FastAPI serializes the exception
    # object itself and the client gets a success status code with an empty body
    except (SSLAValidationException, SSLAFormatException) as e:
        logger.exception("unprocessable SSLA content")
        raise ResponseError(message="unprocessable SSLA content", exception=e,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # any other SSLA level issue (metric, slo, capability, service description)
    except SSLAException as e:
        logger.exception("invalid SSLA")
        raise ResponseError(message="invalid SSLA", exception=e,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
    logger.debug("PUT /ssla")
    ssla_content = await ssla.read()

    try:
        get_spm().update_ssla(ssla_content)
    except SSLANotFound as e:
        logger.warning(f"no SSLA to update: {e}")
        raise ResponseError(message="SSLA not found to update", exception=e, status=status.HTTP_404_NOT_FOUND)
    except (SSLAValidationException, SSLAFormatException) as e:
        logger.exception("unprocessable SSLA content")
        raise ResponseError(message="unprocessable SSLA content", exception=e,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except SSLAException as e:
        logger.exception("invalid SSLA")
        raise ResponseError(message="invalid SSLA", exception=e, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
    except SSLANotFound as e:
        raise ssla_not_found(service, e)

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
                200: {"description": "List of SLOs successfully retrieved from submitted SSLAs",
                      "model": List[SLO]},
                404: {"description": "No SLOs found"}
            })
async def get_slos(service: str):
    logger.debug(f"GET /ssla/slo")
    try:
        slos = get_spm().get_slos_jsonable(service)
    except SSLANotFound as e:
        raise ssla_not_found(service, e)
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
    try:
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
    except SSLANotFound as e:
        raise ssla_not_found(service, e)
    except SSLAMetricsException as e:
        logger.warning(f"no metric '{metric}' in the SSLA of service '{service}': {e}")
        raise ResponseError(message=f"no metric found for service '{service}'", exception=e,
                            status=status.HTTP_404_NOT_FOUND)

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
    try:
        properties = get_spm().get_service_properties_jsonable(service)
    except SSLANotFound as e:
        raise ssla_not_found(service, e)
    serialized_properties: List["ServiceProperties"] = []
    for prop in properties:
        prop_encoded = jsonable_encoder(prop)
        serialized_properties.append(prop_encoded)
    return JSONResponse(content=serialized_properties)
