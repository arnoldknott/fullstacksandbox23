import asyncio
import logging
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

# TBD: this is the one, that starts the celery app in backend_api:
from core.celery_app import celery_app  # noqa: F401
from core.config import config
from core.databases import run_migrations
from core.fastapi import mount_rest_api_routes
from core.socketio import mount_socketio_app, socketio_server
from routers.ws.v1.websockets import router as websocket_router

logger = logging.getLogger(__name__)

# print("Current directory:", os.getcwd())
# print("sys.path:", sys.path)

api_prefix = "/api/v1"
socketio_prefix = "/socketio/v1"
ws_prefix = "/ws/v1"


# TBD: add postgres database:
# context manager does setup and tear down
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configures application startup and shutdown events."""
    logger.info("Application startup")
    # configure_logging()# TBD: add logging configuration
    # Don't do that: use Sessions instead!
    # await postgres.connect()
    asyncio.create_task(run_migrations())
    yield  # this is where the FastAPI runs - when its done, it comes back here and closes down
    # await postgres.disconnect()
    await socketio_server.shutdown()
    logger.info("Application shutdown")




fastapi_app = FastAPI(
    title="backendAPI",
    summary="Backend for fullstack Sandbox.",
    description="Playground for trying out anything freely before using in projects.",  # TBD: add the longer markdown description here
    version="0.0.1",  # TBD: read from CHANGELOG.md or environment variable or so?
    lifespan=lifespan,
    swagger_ui_init_oauth={
        "clientId": config.BACKEND_API_CLIENT_ID,
        "useBasicAuthenticationWithAccessCodeGrant": True,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": [
            # "User.Read",
            "openid",
            "profile",
            f"api://{config.API_SCOPE}/api.read",
            f"api://{config.API_SCOPE}/api.write",
            f"api://{config.API_SCOPE}/socketio",
        ],
    },
    # swagger_ui_parameters=swagger_ui_parameters,
    # TBD: add contact - also through environment variables?
)
print("👍 💨 FastAPI started")


# @app.on_event("shutdown")
# async def shutdown():
#     """Runs when the app stops."""
#     await postgres.disconnect()


fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config.FRONTEND_SVELTE_ORIGIN,
        (
            f"https://{config.FRONTEND_SVELTE_FQDN}:80"
            if config.FRONTEND_SVELTE_FQDN
            else None
        ),
        (
            f"https://{config.FRONTEND_SVELTE_FQDN}"
            if config.FRONTEND_SVELTE_FQDN
            else None
        ),
        (
            "https://admin.socket.io"
            if config.SOCKETIO_ADMIN_USERNAME and config.SOCKETIO_ADMIN_PASSWORD
            else None
        ),
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],  # or ["*"],
    allow_headers=["*"],
)

mount_rest_api_routes(fastapi_app, api_prefix)


fastapi_app.include_router(
    websocket_router,
    prefix=f"{ws_prefix}",
    tags=["Web Sockets"],
    # TBD: consider adding a dependency here for the token
)


# exception handler logs exceptions before passing them to the default exception handler
@fastapi_app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


socketio_app = socketio.ASGIApp(socketio_server, socketio_path=socketio_prefix)
fastapi_app.mount(socketio_prefix, app=socketio_app)

mount_socketio_app(fastapi_app)
