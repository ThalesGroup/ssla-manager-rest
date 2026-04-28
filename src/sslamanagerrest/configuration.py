"""
Orchestrator Configuration
Model implementation of the sslaorchestrator configuration
"""
import os.path
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic import ValidationError
from yaml import YAMLError

from sslamanagerrest.exceptions import ConfigurationMissingException, ConfigurationException


class Server(BaseModel):
    address: str
    port: int


class Configuration(BaseModel):
    server: Server = Field()
    ssla_db: Path

    @classmethod
    def get_config(cls, config_path: Path):
        """
        Parse a config file into this configuration object model
        :param config_path: Path of the configuration file to parse
        :return: The Configuration object model
        """
        if not config_path.is_file():
            raise ConfigurationMissingException(f"Missing configuration file at '{config_path}'")

        with open(config_path, "r") as f:
            try:
                return cls.model_validate(yaml.safe_load(f.read()))
            except (YAMLError, ValidationError) as e:
                raise ConfigurationException(f"Wrong configuration content at '{config_path}", e.args)

    def set_logging_level(self, level: str):
        self.logging.set_level(level)

    def is_debug_enabled(self):
        return "DEBUG" == str.upper(self.logging.level)

    def get_ssla_schema_path(self) -> Path:
        return Path(os.path.abspath(self.ssla_schema))
