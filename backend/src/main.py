import asyncio
import logging
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

# TBD: this is the one, that starts the celery app in backend_api:
from core.celery_app import celery_app  # noqa: F401
from core.config import config
from core.databases import postgres_async_engine, run_migrations
from core.fastapi import attach_middeleware, mount_rest_api_routes
from core.socketio import mount_socketio_app, socketio_server

logger = logging.getLogger(__name__)

api_prefix = "/api/v1"
socketio_prefix = "/socketio/v1"
ws_prefix = "/ws/v1"


# context manager does setup and tear down
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configures application startup and shutdown events."""
    logger.info("Application startup")
    # configure_logging()# TBD: add logging configuration
    asyncio.create_task(run_migrations())
    yield  # this is where the FastAPI runs - when its done, it comes back here and closes down
    logger.info("Application shutdown - closing connections")
    await socketio_server.shutdown()
    await postgres_async_engine.dispose()  # Properly close all database connections
    logger.info("Application shutdown complete")


fastapi_app = FastAPI(
    title="backendAPI",
    summary="Backend for fullstack Sandbox.",
    description="Playground for trying out anything freely before using in projects.",  # TBD: add the longer markdown description here
    version="0.0.1",  # TBD: read from CHANGELOG.md or environment variable or so?
    lifespan=lifespan,
    # swagger_ui_init_oauth={
    swagger_ui_init_oauth={
        "clientId": config.DEVELOPER_CLIENTS_CLIENT_ID,
        "useBasicAuthenticationWithAccessCodeGrant": True,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": [
            # "User.Read",
            "openid",
            "profile",
            f"api://{config.API_SCOPE}/api.read",
            f"api://{config.API_SCOPE}/api.write",
            # f"api://{config.API_SCOPE}/socketio",
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


attach_middeleware(fastapi_app)

mount_rest_api_routes(fastapi_app, api_prefix, ws_prefix)


# exception handler logs exceptions before passing them to the default exception handler
@fastapi_app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


socketio_app = socketio.ASGIApp(socketio_server, socketio_path=socketio_prefix)
fastapi_app.mount(socketio_prefix, app=socketio_app)

mount_socketio_app(fastapi_app)
