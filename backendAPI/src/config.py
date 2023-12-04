import os
from functools import lru_cache
from typing import Any, Dict, Optional

from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings

# from azure.identity import EnvironmentCredential
# from azure.identity import DefaultAzureCredential


# def get_azure_client(vault_url):
#     """Returns an Azure client instance."""
#     credential = DefaultAzureCredential()
#     client = SecretClient(vault_url=vault_url, credential=credential)
#     return client


def get_variable(variable_name):
    """Returns a function that retrieves a variable from the environment."""

    # note: the existence of the environment variable AZURE_KEYVAULT_URL is used to determine whether to use keyvault or not.
    if os.getenv("AZURE_KEYVAULT_HOST"):
        # credential = DefaultAzureCredential()
        # credential = ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID"))
        credential = ManagedIdentityCredential()
        # Following line works, when the environment variable AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET and AZURE_AUTHORITY_HOST are set.
        # credential = EnvironmentCredential()
        client = SecretClient(
            # TBD: check if we need host or URL here?
            vault_url=os.getenv("AZURE_KEYVAULT_HOST"),
            credential=credential,
        )

        def get_variable_inner(variable_name):
            """Returns a variable from the environment."""
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
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: Optional[str] = os.getenv("POSTGRES_HOST")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_URL: Optional[PostgresDsn] = None

    @classmethod
    @field_validator("POSTGRES_URL")
    def build_postgres_url(cls, url: Optional[str], values: Dict[str, Any]) -> Any:
        """Validates and builds the postgres URL."""
        if isinstance(url, PostgresDsn):
            return url
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.POSTGRES_USER,
            password=values.POSTGRES_PASSWORD,
            host=f"/{values.POSTGRES_HOST or 'postgres'}",  # TBD: consider putting the host in an environment variable => it's the container name!
            path=f"/{values.POSTGRES_DB or ''}",
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


@lru_cache(maxsize=None)
def get_config():
    """Returns the configuration instance."""
    # configuration = Config()
    # print(f"POSTGRES_DB: {configuration.POSTGRES_DB}")
    return Config()


config = get_config()
