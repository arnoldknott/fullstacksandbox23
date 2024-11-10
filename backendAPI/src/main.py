import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from socketio import ASGIApp

from core.security import CurrentAccessTokenHasRole, CurrentAccessTokenHasScope
from routers.api.v1.access import router as access_router
from routers.api.v1.category import router as category_router
from routers.api.v1.core import router as core_router
from routers.api.v1.demo_file import router as demo_file_router
from routers.api.v1.demo_resource import router as demo_resource_router
from routers.api.v1.identities import (
    group_router,
    sub_group_router,
    sub_sub_group_router,
    ueber_group_router,
    user_router,
)
from routers.api.v1.protected_resource import router as protected_resource_router
from routers.api.v1.public_resource import router as public_resource_router
from routers.api.v1.tag import router as tag_router
from routers.socketio.v1.base import socketio_server
from routers.socketio.v1.protected_events import ProtectedEvents
from routers.ws.v1.websockets import router as websocket_router

# print("Current directory:", os.getcwd())
# print("sys.path:", sys.path)

# from core.databases import postgres
# from core.databases import mongodb
# from core.cache import redis
# from core.logging import configure_logging

logger = logging.getLogger(__name__)


# TBD: add postgres database:
# context manager does setup and tear down
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configures application startup and shutdown events."""
    logger.info("Application startup")
    # configure_logging()# TBD: add logging configuration
    # Don't do that: use Sessions instead!
    # await postgres.connect()
    yield  # this is where the FastAPI runs - when its done, it comes back here and closes down
    # await postgres.disconnect()
    logger.info("Application shutdown")


# # TBD: add OAuth2AuthorizationCodeBearer, asks for client_id and client_secret
# # needs scopes
# # primarily this is relevant for Swagger UI, API can be accessed by other tools right now, as long as
# # their callback URL is registered in the Azure AD app registration!
# TBD: so far it works until the redirect URL is required:
# here's the documentation for how to implement the redirect URL:
# https://github.com/fastapi/fastapi/blob/0c7296b19ed5cecbafb01a8d0592bcd66e703153/fastapi/applications.py#L447
# => add an endpoint /docs/oauth2-redirect to receive the token.
# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/v2.0/authorize",
#     tokenUrl=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/token",
#     scopes={
#         f"api://{config.API_SCOPE}/api.read": "Read API",
#         f"api://{config.API_SCOPE}/api.write": "Write API",
#     },
#     scheme_name="OAuth2 Authorization Code",
#     description="OAuth2 Authorization Code Bearer implementation for Swagger UI - identity provider is Microsoft Azure AD",
# )

# swagger_ui_parameters = {
#     "oauth2RedirectUrl": "http://localhost:8000/oauth/callback",  # replace with your actual callback URL
# }

# or:
# swagger_ui_parameters = {
#     "network": {
#         "oauth2RedirectUrl": "http://localhost:8000/oauth/callback",  # replace with your actual callback URL
#     }
# }

# TBD consider moving to router?
api_prefix = "/api/v1"
ws_prefix = "/ws/v1"

app = FastAPI(
    title="backendAPI",
    summary="Backend for fullstack Sandbox.",
    description="Playground for trying out anything freely before using in projects.",  # TBD: add the longer markdown description here
    version="0.0.1",  # TBD: read from CHANGELOG.md or environment variable or so?
    lifespan=lifespan,
    # swagger_ui_parameters=swagger_ui_parameters,
    # TBD: add contact - also through environment variables?
)


### DEPRECTATED: use lifespan instead
# @app.on_event("startup")
# async def startup():
#     """Runs when the app starts."""
#     # configure_logging()# TBD: add logging configuration
#     SQLModel.metadata.create_all(postgres)


# @app.on_event("shutdown")
# async def shutdown():
#     """Runs when the app stops."""
#     await postgres.disconnect()

# TBD: no using underscores in routes - slashes instead, so nested routers. Or dashes. no uppercase letters either!
# app.include_router(oauth_router, tags=["OAuth"])
app.include_router(core_router, prefix=f"{api_prefix}/core", tags=["Core"])
app.include_router(
    user_router,
    prefix=f"{api_prefix}/user",
    tags=["User"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
)

app.include_router(
    ueber_group_router,
    prefix=f"{api_prefix}/uebergroup",
    tags=["Ueber Group"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
)

app.include_router(
    group_router,
    prefix=f"{api_prefix}/group",
    tags=["Group"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
)

app.include_router(
    sub_group_router,
    prefix=f"{api_prefix}/subgroup",
    tags=["Sub Group"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
)

app.include_router(
    sub_sub_group_router,
    prefix=f"{api_prefix}/subsubgroup",
    tags=["Sub-sub Group"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
)

app.include_router(
    access_router,
    prefix=f"{api_prefix}/access",
    tags=["Access"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
)
app.include_router(
    public_resource_router,
    prefix=f"{api_prefix}/publicresource",
    tags=["Public Resource"],
)

app.include_router(
    demo_resource_router,
    prefix=f"{api_prefix}/demoresource",
    tags=["Demo Resource"],
)

app.include_router(
    demo_file_router,
    prefix=f"{api_prefix}/demo",
    tags=["Demo File"],
    dependencies=[Depends(CurrentAccessTokenHasRole("User"))],
)


app.include_router(
    category_router,
    prefix=f"{api_prefix}/category",
    tags=["Category"],
)
app.include_router(
    tag_router,
    prefix=f"{api_prefix}/tag",
    tags=["Tag"],
)
# checked_scopes = ScopeChecker(["api.read", "api.write"])
# protected_scopes = ScopeChecker(["api.read"])
app.include_router(
    protected_resource_router,
    prefix=f"{api_prefix}/protected",
    tags=["Protected Resource"],
    dependencies=[Depends(CurrentAccessTokenHasScope("api.read"))],
    # TBD: This is not ready to use - requires the redirect URI to be passed through Swagger UI
    # dependencies=[Depends(oauth2_scheme)],
)
# course_scopes = ScopeChecker(
#     ["api.read", "api.write"]
# )  # add artificial.read, artificial.write, mapped_account.read, mapped_account.write, ...
# app.include_router(
#     access_control_router,
#     prefix=f"{api_prefix}/access",
#     tags=["Access Control"],
#     # dependencies=[Depends(course_scopes)],
# )
# Sign-up is handled by security - controlled by token content!
# TBD: this can be implemented later for admin dashboard or so.

app.include_router(
    websocket_router,
    prefix=f"{ws_prefix}",
    tags=["Web Sockets"],
    # TBD: consider adding a dependency here for the token
)

socketio_server.register_namespace(ProtectedEvents("/protected_events"))
socketio_app = ASGIApp(socketio_server, socketio_path="socketio/v1")
app.mount("/socketio/v1", app=socketio_app)


# exception handler logs exceptions before passing them to the default exception handler
@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
