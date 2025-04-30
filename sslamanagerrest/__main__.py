import argparse
import json
import logging
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from sslamanagerrest import api
from sslamanagerrest.configuration import Configuration
from sslamanagerrest.environment import set_configuration_path, get_configuration, get_configuration_path, get_spm
from sslamanagerrest.exceptions import ConfigurationMissingException

LOGGING_FORMAT = "%(asctime)s - (%(filename)s:%(lineno)d) - %(levelname)s - %(message)s"

app = FastAPI()
app.include_router(api.router)
app.title = "SSLA Manager API"
app.description = "REST API for the ecurity Policy Manager"

logger: logging.Logger

SPM_CONFIGURATION_PATH = "SPM_CONFIGURATION_PATH"


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
    global logger
    logger = logging.getLogger("uvicorn.default")
    level = "DEBUG" if debug else "INFO"
    logger.setLevel(level=level)
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
    with open(f'{current_dir}/../openapi.json', 'w') as f:

        json.dump(get_openapi(
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
