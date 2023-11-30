import os
from functools import lru_cache

from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
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
    if os.getenv("AZURE_KEYVAULT_URL"):
        # credential = DefaultAzureCredential()
        # credential = ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID"))
        credential = ManagedIdentityCredential()
        # Following line works, when the environment variable AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET and AZURE_AUTHORITY_HOST are set.
        # credential = EnvironmentCredential()
        client = SecretClient(
            vault_url=os.getenv("AZURE_KEYVAULT_URL"), credential=credential
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
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    # get those variables from keyvault if keyvault URL is set, otherwise get from environment:
    test_secret: str = get_variable("test-secret")
    print(f"test_secret: {test_secret}")

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
