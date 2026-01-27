from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config
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
from routers.api.v1.presentation import router as presentation_router
from routers.api.v1.quiz import router as quiz_router
from routers.ws.v1.websockets import router as websocket_router


def attach_middeleware(app: FastAPI):
    """Attaches middleware to the FastAPI application."""
    app.add_middleware(
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


def mount_rest_api_routes(app: FastAPI, api_prefix: str, ws_prefix: str):
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
    app.include_router(
        presentation_router,
        prefix=f"{api_prefix}/presentation",
        tags=["Presentation"],
    )
    app.include_router(
        quiz_router,
        prefix=f"{api_prefix}/quiz",
        tags=["Quiz"],
    )
    app.include_router(
        websocket_router,
        prefix=f"{ws_prefix}",
        tags=["Web Sockets"],
        # TBD: consider adding a dependency here for the token
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
