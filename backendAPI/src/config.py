import os
from functools import lru_cache

from azure.identity import DefaultAzureCredential, SecretClient
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Base configuration class."""

    ENVIRONMENT: str = os.getenv("ENVIRONMENT")


def select_variable_set(environment: str) -> str:
    """Selects the variable set to use from environment."""
    if environment == "development":
        return "DEV_"
    elif environment == "test":
        return "TEST_"
    else:
        raise ValueError(
            f"Invalid environment variable: {environment}."
            f"Must be one of: ['development', 'test']"
        )


class DevelopmentConfig(Config):
    """Development configuration class."""

    prefix = select_variable_set("development")
    POSTGRES_USER: str = os.getenv(f"{prefix}POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv(f"{prefix}POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv(f"{prefix}POSTGRES_DB")
    REDIS_HOST: str = os.getenv(f"{prefix}REDIS_HOST")
    REDIS_PORT: int = os.getenv(f"{prefix}REDIS_PORT")
    MONGODB_HOST: str = os.getenv(f"{prefix}MONGODB_HOST")
    MONGODB_PORT: int = os.getenv(f"{prefix}MONGODB_PORT")


class TestingConfig(DevelopmentConfig):
    """Testing configuration class."""

    prefix = select_variable_set("test")


def get_azure_client(vault_url):
    """Returns an Azure client instance."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client


class StagingConfig(Config):
    """Staging configuration class."""

    client = get_azure_client(os.getenv("STAGING_AZURE_KEYVAULT_URL"))
    POSTGRES_USER: str = client.get_secret("postgres-user").value
    POSTGRES_PASSWORD: str = client.get_secret("postgres-password").value
    POSTGRES_DB: str = client.get_secret("postgres-db").value
    REDIS_HOST: str = client.get_secret("redis-host").value
    REDIS_PORT: int = client.get_secret("redis-port").value
    MONGODB_HOST: str = client.get_secret("mongodb-host").value
    MONGODB_PORT: int = client.get_secret("mongodb-port").value


class ProductionConfig(StagingConfig):
    """Production configuration class."""

    client = get_azure_client(os.getenv("PRODUCTION_AZURE_KEYVAULT_URL"))


config_classes = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}


@lru_cache(maxsize=None)
def get_active_config():
    config_class = config_classes[os.getenv("ENVIRONMENT")]
    return config_class()


active_config = get_active_config()
