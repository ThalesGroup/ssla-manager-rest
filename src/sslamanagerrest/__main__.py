import argparse
import json
import logging
import os
import sys

import uvicorn
import yaml
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from sslamanagerrest import api
from sslamanagerrest.configuration import Configuration
from sslamanagerrest.environment import set_configuration_path, get_configuration, get_configuration_path, get_spm
from sslamanagerrest.exceptions import ConfigurationMissingException
from sslamanagerrest.route.response import format_exception_chain

LOGGING_FORMAT = "%(asctime)s - (%(filename)s:%(lineno)d) - %(levelname)s - %(message)s"
# the rest api and the ssla-manager dependency: both must reach the console, otherwise
# the parsing errors logged inside the library are silently dropped by the root logger
LOGGED_PACKAGES = ("sslamanagerrest", "sslamanager")

app = FastAPI()
app.include_router(api.router)
app.title = "SSLA Manager API"
app.description = "REST API for the ecurity Policy Manager"

logger: logging.Logger = logging.getLogger("sslamanagerrest.main")

SPM_CONFIGURATION_PATH = "SPM_CONFIGURATION_PATH"


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: "Request", exception: Exception) -> "JSONResponse":
    """
    Last resort handler: log the full traceback and return the error chain instead of
    an empty '500 Internal Server Error' body.
    """
    logger.exception(f"unhandled error on {request.method} {request.url.path}")
    detail = {"message": "internal server error",
              "error": type(exception).__name__,
              "reason": str(exception),
              "causes": format_exception_chain(exception)[1:]}
    return JSONResponse(content={"detail": detail}, status_code=500)


class Parser:
    parser: argparse.ArgumentParser

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser
        # Verbose is True or None on purpose :
        #   - if provided, enable debug level
        #   - if not provided, keep the level configured in the configuration file
        self.parser.add_argument('-c', '--configuration', action='store', dest='configuration',
                                 required=True, help='Path to the SSLA orchestrator configuration file')
        self.parser.add_argument('--dump-openapi', action='store_true', dest='dump_openapi',
                                 help='Extract the OpenApi v3 spec file without running the server')
        self.parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                                 help='Set verbose mode to enable debug log level')

    def get_arguments(self):
        return self.parser.parse_args()


def init_logger(debug: bool):
    """
    Attach a console handler to the application and dependency loggers.
    Done here rather than through the uvicorn log config so that logs emitted before the
    server starts, and logs of the ssla-manager dependency, are printed as well.
    """
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    for package in LOGGED_PACKAGES:
        package_logger = logging.getLogger(package)
        package_logger.setLevel(level)
        package_logger.handlers.clear()
        package_logger.addHandler(handler)
        # uvicorn owns the root logger configuration, do not duplicate records there
        package_logger.propagate = False
    logger.debug("Debug logs enabled")


def init_environment(args):
    set_configuration_path(args.configuration)
    # init database and check for proper instantiation
    spm = get_spm()
    if spm is None:
        logger.error("cannot create the SSLA manager")
        sys.exit(1)


def dump_openapi_spec():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f'{current_dir}/../../openapi.yaml', 'w') as f:

        yaml.dump(get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes
        ), f)


def check_args(args):
    if args.dump_openapi:
        dump_openapi_spec()
        sys.exit(0)
    else:
        pass


def main():
    """
    Launch the app and startup the server.
    The Application arguments are parsed.
    The Application Environment MUST be initialized before startup.
    """
    # application
    parser = Parser(argparse.ArgumentParser())
    args = parser.get_arguments()
    check_args(args)
    init_logger(args.verbose)
    init_environment(args)

    # configuration
    configuration: "Configuration"
    try:
        configuration = get_configuration()
    except ConfigurationMissingException:
        logger.error(f"Configuration not found in '{get_configuration_path()}'")
        sys.exit(1)

    # server logger
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = LOGGING_FORMAT
    log_config["formatters"]["default"]["fmt"] = LOGGING_FORMAT

    # server start
    host = configuration.server.address
    port = configuration.server.port
    uvicorn.run(app, host=host, port=port, log_config=log_config)


if __name__ == "__main__":
    main()
