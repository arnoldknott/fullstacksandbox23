import logging
import os
from functools import lru_cache
from time import sleep
from typing import Any, Optional

from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings

# from azure.identity import EnvironmentCredential
# from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

# def get_azure_client(vault_url):
#     """Returns an Azure client instance."""
#     credential = DefaultAzureCredential()
#     client = SecretClient(vault_url=vault_url, credential=credential)
#     return client


def get_variable(variable_name):
    """Returns a function that retrieves a variable from the environment."""

    # note: the existence of the environment variable AZURE_KEYVAULT_URL is used to determine whether to use keyvault or not.
    if os.getenv("AZ_KEYVAULT_HOST"):
        # credential = DefaultAzureCredential()
        # credential = ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID"))
        credential = ManagedIdentityCredential()
        # Following line works, when the environment variable AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET and AZURE_AUTHORITY_HOST are set.
        # credential = EnvironmentCredential()
        logger.info("Accessing keyvault")
        print("== AZ_KEYVAULT_HOST ==")
        print(os.getenv("AZ_KEYVAULT_HOST"))
        client = SecretClient(
            # TBD: check if we need host or URL here?
            vault_url=os.getenv("AZ_KEYVAULT_HOST"),
            credential=credential,
        )

        def get_variable_inner(variable_name):
            """Returns a variable from the environment."""
            logger.info(f"Getting variable ${variable_name} from keyvault")
            variable_name = variable_name.replace("_", "-").lower()
            return client.get_secret(variable_name).value

    else:

        def get_variable_inner(variable_name):
            """Returns a variable from the environment."""
            return os.getenv(variable_name)

    return get_variable_inner(variable_name)


class Config(BaseSettings):
    """Base configuration class."""

    # always get those variables from the environment:
    # TBD: refactor:     this should no longer be necessary from the environment since database is now an Azure postgres database:
    POSTGRES_HOST: Optional[str] = os.getenv("POSTGRES_HOST")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_URL: Optional[PostgresDsn] = None  # Field(None, validate_default=True)

    # TBD: set these variables in terraform!
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    print("=== REDIS_PORT ===")
    print(REDIS_PORT)
    print("=== get_variable('REDIS_REDIS_JWKS_DB') ===")
    print(get_variable("REDIS_JWKS_DB"))
    REDIS_JWKS_DB: int = int(get_variable("REDIS_JWKS_DB"))
    REDIS_PASSWORD: str = get_variable("REDIS_PASSWORD")

    @field_validator("POSTGRES_URL")
    @classmethod
    def build_postgres_url(cls, url: Optional[str], values: ValidationInfo) -> Any:
        """Validates and builds the postgres URL."""
        # print("Building postgres URL")
        logger.info("Building postgres URL")
        if isinstance(url, str):
            return url
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data["POSTGRES_USER"],
            password=values.data["POSTGRES_PASSWORD"],
            # "postgres" is the container name
            host=values.data["POSTGRES_HOST"] or "postgres",
            # port=values.data["POSTGRES_PORT"] or 5432,
            path=values.data["POSTGRES_DB"] or "",
        )

    # get those variables from keyvault if keyvault URL is set, otherwise get from environment:
    KEYVAULT_HEALTH: str = get_variable("KEYVAULT_HEALTH")
    # TEST_SECRET1: str = get_variable("TEST_SECRET1")
    # TEST_SECRET2: str = get_variable("TEST_SECRET2")
    # print(f"test_secret: {TEST_SECRET2}")

    # not in keyvault yet:
    # REDIS_HOST: str = get_variable("REDIS_HOST")
    # REDIS_PORT: int = get_variable("REDIS_PORT")

    # MONGODB_HOST: str = get_variable("MONGODB_HOST")
    # MONGODB_PORT: int = get_variable("MONGODB_PORT")


def update_config(tries=0):
    """Updates the configuration instance waits 5 seconds and retries 10 times if necessary."""
    logger.info("Updating configuration")
    try:
        return Config()
    except Exception as err:
        tries += 1
        if tries < 10:
            logger.info(
                f"Try {tries} failed to update configuration, retrying in 5 seconds."
            )
            sleep(5)
            return update_config(tries)
        else:
            logger.error(f"Failed to update configuration after {tries} tries.")
            raise err


@lru_cache(maxsize=None)
def get_config():
    """Returns the configuration instance."""
    # print("Configuration called")
    logger.info("Configuration called")
    # configuration = Config()
    # print(f"POSTGRES_DB: {configuration.POSTGRES_DB}")
    # return Config()
    return update_config()


config = get_config()
