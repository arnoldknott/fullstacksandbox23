import logging
from contextlib import asynccontextmanager

from core.security import guards
from fastapi import Depends, FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from routers.api.v1.access_control import router as access_control_router
from routers.api.v1.category import router as category_router
from routers.api.v1.core import router as core_router
from routers.api.v1.demo_resource import router as demo_resource_router
from routers.api.v1.protected_resource import router as protected_resource_router
from routers.api.v1.tag import router as tag_router
from routers.api.v1.user import router as user_router

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


# TBD consider moving to router?
global_prefix = "/api/v1"

app = FastAPI(
    title="backendAPI",
    summary="Backend for fullstack Sandbox.",
    description="Playground for trying out anything freely before using in projects.",  # TBD: add the longer markdown description here
    version="0.0.1",  # TBD: read from CHANGELOG.md or environment variable or so?
    lifespan=lifespan,
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
app.include_router(core_router, prefix=f"{global_prefix}/core", tags=["Core"])
app.include_router(
    demo_resource_router,
    prefix=f"{global_prefix}/demo_resource",
    tags=["Demo Resource"],
)


app.include_router(
    category_router,
    prefix=f"{global_prefix}/category",
    tags=["Category"],
)
app.include_router(
    tag_router,
    prefix=f"{global_prefix}/tag",
    tags=["Tag"],
)
# checked_scopes = ScopeChecker(["api.read", "api.write"])
# protected_scopes = ScopeChecker(["api.read"])
app.include_router(
    protected_resource_router,
    prefix=f"{global_prefix}/protected_resource",
    tags=["Protected Resource"],
    # dependencies=[Depends(protected_scopes)],
)
# course_scopes = ScopeChecker(
#     ["api.read", "api.write"]
# )  # add artificial.read, artificial.write, mapped_account.read, mapped_account.write, ...
app.include_router(
    access_control_router,
    prefix=f"{global_prefix}/access",
    tags=["Access Control"],
    # dependencies=[Depends(course_scopes)],
)
app.include_router(
    user_router,
    prefix=f"{global_prefix}/user",
    tags=["User"],
    dependencies=[Depends(guards.current_token_has_scope_api_write)],
)


# exception handler logs exceptions before passing them to the default exception handler
@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
