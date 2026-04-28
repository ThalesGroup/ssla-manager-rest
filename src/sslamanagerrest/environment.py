"""
FastAPI global dependencies
Declare here the dependencies for the REST API core.api.routers
The @lru_cache decorator on a method is used to load an object only once per runtime :
  - the first time the method is called, the configuration is loaded inside the memory and returned as result
  - The second time the method is called (and the other times after that), the configuration previously loaded is
    returned directly from the memory without any additional loading.
"""
import logging
import os
from functools import lru_cache
from pathlib import Path

from sslamanager.api import SecurityPolicyManager

from sslamanagerrest.configuration import Configuration

logger = logging.getLogger("uvicorn.default")

SPM_CONFIGURATION_PATH = "SPM_CONFIGURATION_PATH"


def set_configuration_path(path: str):
    os.environ[SPM_CONFIGURATION_PATH] = path


@lru_cache
def get_configuration_path() -> "str":
    """
    This method loads in memory the configuration path and returns it as a result.
    Use this method any time you need the configuration path
    :return: the path of the configuration
    """
    return os.getenv(SPM_CONFIGURATION_PATH)


@lru_cache
def get_configuration() -> "Configuration":
    """
    This method loads in memory the configuration object and returns it as a result.
    Use this method any time you need the configuration.
    :return: the configuration
    """
    return Configuration.get_config(Path(get_configuration_path()))


@lru_cache
def get_configuration_from_path(path: Path) -> "Configuration":
    """
    This method loads in memory the configuration object and returns it as a result.
    Use this method any time you need the configuration.
    :return: the configuration
    """
    return Configuration.get_config(path)


@lru_cache
def get_spm() -> "SecurityPolicyManager":
    return SecurityPolicyManager(get_configuration().ssla_db)
