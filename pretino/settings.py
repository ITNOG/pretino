"""App settings module"""

from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Union

from pydantic import BaseModel, Json
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevels(str, Enum):
    """
    Supported log levels
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    ERROR = "ERROR"


class ApiKey(BaseModel):
    """
    User model
    """

    key: str
    privileged: bool = False


class QuestionMapping(BaseSettings):
    """
    Supported questions
    """

    company: str
    job_title: str
    bio_url: str
    asn: str
    tshirt_size: str
    food_intolerance: str


class Settings(BaseSettings):
    """
    App settings model
    """

    ORGANIZER: str
    EVENT_NAME: str
    API_TOKEN: str
    QUESTION_MAPPING: Json[QuestionMapping]
    HOST: Union[IPv4Address, IPv6Address] = "127.0.0.1"
    PORT: int = 8000
    LOGLEVEL: LogLevels = LogLevels.INFO
    API_KEYS: list[ApiKey] = []

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="PRETINO_"
    )
