import logging
from typing import Annotated

import httpx
from core.access import get_token_from_header
from core.config import config
from fastapi import APIRouter, Header
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)
router = APIRouter()


confClientApp = ConfidentialClientApplication(
    config.AZURE_CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",
    client_credential=config.BACK_CLIENT_SECRET,
)


def get_users_groups_ms_graph(access_token: str):
    """Dummy function to try if access token works from backend"""
    # response = httpx.get("https://graph.microsoft.com/v1.0/me/transitiveMemberOf", headers = {"Authorization": f"Bearer {access_token}"})
    response = httpx.get(
        "https://graph.microsoft.com/v1.0/me/transitiveMemberOf",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    groups = response.json()
    print("=== groups ===")
    print(groups)
    return groups


@router.get("/health")
async def get_health():
    """Returns a 200 OK."""
    logger.info("Health check")
    return {"status": "ok"}


# @router.get("/version")
# async def version():
#     """Returns the version of the backendAPI."""
#     logger.info("Version check")
#     return {"version": "0.0.1"}


@router.get("/keyvault")
async def get_keyvault():
    """Returns the configuration of the Azure keyvault."""
    logger.info("Keyvault check")
    return {
        "Azure keyvault status": config.KEYVAULT_HEALTH,
    }


# Note: this one is protected under the scope "user_impersonization"" from https://management.azure.com
# Cannot scopes from other audiences, like this backendAPI.
@router.get("/onbehalfof")
async def get_onbehalfof(authorization: Annotated[str | None, Header()] = None):
    """Access Microsoft Graph as downstream API on behalf of the user."""
    # print("=== authorization ===")
    # print(authorization)
    token = get_token_from_header(authorization)
    logger.info("🔑 Acquiring token on behalf of")
    print("=== getting token on behalf of ===")
    result = confClientApp.acquire_token_on_behalf_of(
        token,
        scopes=["User.Read"]
        # scopes=[
        #     "api.read"
        # ],  # ["User.Read", "https://management.azure.com/user_impersonation"],
    )
    # print("=== result ===")
    # print(result)
    try:
        if "access_token" in result:
            logger.info("🔑 Getting user information on behalf of")
            on_behalf_of_token = result["access_token"]
            response = get_users_groups_ms_graph(on_behalf_of_token)
            logger.info("On behalf of access to Microsoft Graph")
            return {"body": response}
    except Exception as err:
        logger.error("🔑 Failed to fetch user groups from Microsoft Graph.")
        raise err
