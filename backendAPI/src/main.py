import logging

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from routers.system import router as system_router

# from dependencies.databases import postgres


# from src.dependencies.databases import mongodb
# from src.dependencies.cache import redis
# from src.dependencies.logging import configure_logging

logger = logging.getLogger(__name__)

# print(f"POSTGRES_DB: {config.POSTGRES_DB}")
# print(f"POSTGRES_USER: {config.POSTGRES_USER}")


# TBD: add postgres database:
# context manager does setup and tear down
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Awaits the database when the app starts and disconnects when it stops."""
#     # configure_logging()# TBD: add logging configuration
#     await postgres.connect()
#     yield  # this is where the FastAPI runs - when its done, it comes back here and closes down
#     await postgres.disconnect()

# app = FastAPI(lifespan=lifespan)

global_prefix = "/api/v1"

app = FastAPI(
    title="backendAPI",
    summary="Backend for fullstack Sandbox.",
    description="Handling user authentication and session handling.",  # TBD: add the longer markdown description here
    version="0.0.1",  # TBD: read from CHANGELOG.md or environment variable or so?
    # TBD: add contact - also through environment variables?
)
app.include_router(system_router, prefix=f"{global_prefix}/system")


# exception handler logs exceptions before passing them to the default exception handler
@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
