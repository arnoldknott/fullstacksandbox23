import logging
from pprint import pprint

import socketio

# import core.security
from core.security import get_http_access_token_payload
from fastapi import Request, Depends  # , FastAPI

from dependencies.fastapi_with_socketio.applications import FastAPIwithSocketIO

# from fastapi import APIRouter
from dependencies.fastapi_with_socketio.routing import (
    APIRouterWithSocketIO as APIRouter,
)
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import solve_dependencies

# from fastapi.routing import run_endpoint_function

# from main import app

from core.types import GuardTypes

logger = logging.getLogger(__name__)
router = APIRouter()


# Dummy dependency:
# TBD add a real dependency: , payload=Depends(provide_http_token_payload)
# async def dummy_dependency(input: str | None = None, request: Request | None = None):
async def dummy_dependency(request: Request | None = None):
    """Dummy dependency for testing."""
    # input_header = request.headers.get("Input")
    # print("=== routers - socketio - v1 - dummy_dependency - input ===")
    # print(input)
    print("=== routers - socketio - v1 - dummy_dependency - request ===")
    pprint(request)
    content_type = request.headers.get("content-type")
    print("=== routers - socketio - v1 - dummy_dependency - content_type ===")
    pprint(content_type)
    # print("=== routers - socketio - v1 - dummy_dependency - request.headers ===")
    # print(request.query_string.get())
    # print("=== routers - socketio - v1 - dummy_dependency - payload ===")
    # print(payload)
    # return input + " " + input_header + " output_dummy"
    return "Received content-type: " + content_type + " output_dummy"


# async def provide_dummy_dependency(dummy_response=Depends(dummy_dependency)):
async def provide_dummy_dependency(request: Request | None = None):
    """Provide a dummy dependency for testing."""
    dummy_response = await dummy_dependency(request)
    print("=== routers - socketio - v1 - provide_dummy_dependency - dummy_response ===")
    print(dummy_response)
    return dummy_response


# async def dependency_adapter(dependency, *args, **kwargs):
#     """Provides and adopter to any FastAPI dependency: the dependency is passed in as first argument and it's arguments follow."""
#     # Create a dummy request object - to be able to use the dependency
#     # FastAPI dependencies rely on request response - pattern
#     # TBD: add Query, Path, Body, Header, Cookie, File, Form, Security
#     request = Request(scope={"type": "http"})
#     # Use FastAPI Depends to resolve the dependency
#     resolved = await dependency(
#         dependency=Depends(dependency), request=request, *args, **kwargs
#     )
#     return resolved


# move to main or core.middleware if relevant in other apps:


async def resolve_dependency(dependency, request: Request, *args, **kwargs):
    """Resolve a FastAPI dependency."""
    # route = APIRoute(path="/", endpoint=lambda: None, response_model=None)
    # dependency = Depends(dependency)
    print("=== routers - socketio - v1 - resolve_dependency - *args ===")
    print(*args)
    print("=== routers - socketio - v1 - resolve_dependency - **kwargs ===")
    print(*kwargs)
    dependant = Dependant(call=dependency, path_params={}, request_param_name="request")
    solved_result = await solve_dependencies(
        request=request,
        dependant=dependant,
        body=None,
        async_exit_stack=None,
        embed_body_fields=None,
        # dependency_overrides_provider=app,
    )
    # response = await dependant.call(*args, **solved_result.values)
    response = await dependant.call(**solved_result.values)
    # response = await run_endpoint_function(
    #     dependant=dependant, values=solved_result.values, is_coroutine=True
    # )
    return response


# class SocketIOApp(socketio.ASGIApp):
class SocketIOServer(socketio.AsyncServer):
    """Socket.io server class to handle all common functionality for all namespaces."""

    # def __init__(self, app: FastAPI):
    def __init__(self, app: FastAPIwithSocketIO):
        """Initialize the SocketIOApp."""
        super().__init__(async_mode="asgi")
        self.app = app

    # # This will be an imported function from core.security
    # async def dummy_dependency_socketio_server(self, request: Request | None = None):
    #     """Dummy dependency for testing."""
    #     content_type = request.headers.get("content-type")
    #     print(
    #         "=== routers - socketio - v1 - base - SocketIOServer - dummy_dependency_socketio_server - content_type ==="
    #     )
    #     print(content_type)
    #     return (
    #         "Received content-type: " + content_type + " output_dummy_socketio_server"
    #     )

    # # This will be an imported function from core.security
    # async def provide_dummy_dependency_socketio_server(
    #     self, request: Request | None = None
    # ):
    #     """Provide a dummy dependency for testing."""
    #     dummy_response = await dummy_dependency(request)
    #     print(
    #         "=== routers - socketio - v1 - base - SocketIOServer - provide_dummy_dependency_socketio_server - dummy_response ==="
    #     )
    #     print(dummy_response)
    #     return dummy_response

    async def resolve_dependency_socketio_server(
        self, dependency, request: Request, *args, **kwargs
    ):
        """Resolve a FastAPI dependency."""
        # route = APIRoute(path="/", endpoint=lambda: None, response_model=None)
        # dependency = Depends(dependency)
        # print("=== routers - socketio - v1 - resolve_dependency_socketio_server - *args ===")
        # print(*args)
        # print("=== routers - socketio - v1 - resolve_dependency_socketio_server - **kwargs ===")
        # print(*kwargs)
        dependant = Dependant(
            call=dependency, path_params={}, request_param_name="request"
        )
        solved_result = await solve_dependencies(
            request=request,
            dependant=dependant,
            body=None,
            async_exit_stack=None,
            embed_body_fields=None,
            dependency_overrides_provider=self.app,
        )
        # response = await dependant.call(*args, **solved_result.values)
        response = await dependant.call(**solved_result.values)
        return response


socketio_server = socketio.AsyncServer(async_mode="asgi")
#     async_mode="asgi", logger=True, engineio_logger=True
# )

# print("=== routers - socketio - v1 - vars(socketio_server) ===")
# pprint(vars(socketio_server))
# print("=== routers - socketio - v1 - dir(socketio_server) ===")
# pprint(dir(socketio_server))
# print("=== routers - socketio - v1 - var(socketio_app) ===")
# pprint(socketio_app)
# print("=== routers - socketio - v1 - dir(socketio_app) ===")
# pprint(dir(socketio_app))
# print("=== routers - socketio - v1 - flush ===", flush=True)


# TBD: add auth as FastAPI Depends
@socketio_server.event
async def connect(sid, environ, auth):
    """Connect event for socket.io."""
    logger.info(f"Client connected with session id: {sid}.")
    print("=== routers - socketio - v1 - connect - sid ===", flush=True)
    print(sid, flush=True)
    print("=== routers - socketio - v1 - environ ===", flush=True)
    pprint(environ)
    print("=== routers - socketio - v1 - environ ===", flush=True)
    pprint(auth)
    await socketio_server.emit("message", f"Hello new client with session id {sid}")
    # TBD: add rooms and namespaces?
    # TBD: or refuse connection
    # for example if authentication is not successful:
    # raise ConnectionRefusedError("Connection refused")


@socketio_server.event
async def disconnect(sid):
    """Disconnect event for socket.io."""
    logger.info(f"Client with session id {sid} disconnected.")
    print("=== routers - socketio - v1 - disconnect - sid ===")
    print(sid)


@socketio_server.on("*")
async def catch_all(event, sid, data):
    """Catch all events for socket.io, that don't have an event handler defined."""
    logger.info(f"Caught event {data} from client {sid}.")
    print("=== routers - socketio - v1 - catch_all - event ===")
    print(event)
    print("=== routers - socketio - v1 - catch_all - sid ===")
    print(sid)
    print("=== routers - socketio - v1 - catch_all - data ===")
    print(data)


@socketio_server.event
# @router.socketio("/demo_events")
async def demo_message(sid, data):
    """Demo message event for socket.io."""
    print("=== demo_events - demo_message ===", flush=True)
    logger.info(f"Received message from client {sid}: {data}")
    await socketio_server.emit("demo_message", f"Message received from client: {data}")


# @socketio_server.event(namespace="/protected_events")
# async def protected_message(sid, data):
#     """Protected message event for socket.io."""
#     logger.info(f"Received protected message from client {sid}: {data}")
#     await socketio_server.emit(
#         "protected_message",
#         f"Protected message received from client: {data}",
#         namespace="/protected_events",
#     )


class BaseEvents(socketio.AsyncNamespace):
    """Base class for socket.io namespaces."""

    def __init__(
        self,
        socketio_server: socketio.AsyncServer,
        namespace: str = None,
        guards: GuardTypes = None,
        crud=None,
    ):
        super().__init__(namespace=namespace)
        self.guards = guards
        self.crud = crud
        self.server = socketio_server

    async def authentication(self, auth):
        """Authenticate the client."""
        # token_payload = await get_azure_token_payload(auth)
        # current_user = await check_token_against_guards(token_payload, self.guards)
        # return current_user
        print("=== base - authentication - auth ===")
        print(auth, flush=True)
        return auth

    # TBD: getting there would be really good:
    # @app.socketio("/namespace")
    # should be equal to this:
    # @router.socketio("/namespace")
    # and it should enable that:
    @router.socketio("/namespace")
    async def on_connect(
        self,
        sid,
        environ,
        auth=None,
        token_payload=Depends(get_http_access_token_payload),
        guards=GuardTypes(scopes=["sockets.write"], roles=["User"]),
    ):
        # async def on_connect(
        #     self,
        #     sid,
        #     environ,
        #     auth=None,
        #     # guards,
        #     token_payload=Depends(get_http_access_token_payload),
        #     # dummy_dependency=Depends(dependency_adapter(dummy_dependency, "input_dummy")),
        # ):
        """Connect event for socket.io namespaces."""
        # dummy_response = await dependency_adapter(dummy_dependency, "input_dummy")
        scope = {
            "type": "http",
            "query_string": b"",
            # "headers": [{"Authorization": "input_dummy_header"}],
            # "headers": [],
            "headers": [
                [b"Authorization", b"Bearer scope_dummy_token"],
                [b"content-type", b"text/plain"],
            ],
            "path": "/",
            "method": "GET",
        }
        request = Request(scope=scope)
        resolved_dependency = await self.server.resolve_dependency_socketio_server(
            provide_dummy_dependency, request
        )
        # resolved_dependency = await resolve_dependency(
        #     dummy_dependency,
        #     request,
        #     # "input_dummy",
        #     # keyword_dummy="input_keyword_dummy",
        # )
        print("=== base - on_connect - resolved_dependency ===")
        print(resolved_dependency, flush=True)
        # result = await dummy_dependency("input_dummy", request)
        # print("=== base - on_connect - result ===")
        # print(result, flush=True)
        guards = self.guards
        print("=== base - on_connect - sid ===")
        print(sid, flush=True)
        # print("=== base - on_connect - environ ===")
        # pprint(environ)
        print("=== base - on_connect - auth ===")
        print(auth, flush=True)
        print("=== base - on_connect - guards ===")
        print(guards, flush=True)
        current_user = await self.authentication(auth)
        # logger.info(f"Client connected with session id: {sid}.")
        # token_payload = await get_azure_token_payload(auth)
        print("=== base - on_connect - token_payload ===")
        pprint(token_payload)
        print("=== base - on_connect - guards ===")
        pprint(guards)
        # current_user = await check_token_against_guards(token_payload, guards)
        print("=== base - on_connect - current_user ===")
        print(current_user, flush=True)
        # token_payload = await get_http_access_token_payload(auth)
        # current_user = await check_token_against_guards(token_payload, self.guards)
        # print("=== base - on_connect - sid - current_user ===")
        # print(current_user, flush=True)
        await self.server.emit("message", f"Hello new client with session id {sid}")

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")


# class ProtectedEvents(BaseEvents):
#     """Protected class for socket.io namespaces."""

#     def __init__(self):
#         super().__init__(
#             namespace="/protected_events",
#             guards=GuardTypes(scopes=["sockets.write"], roles=["User"]),
#         )

#     async def on_protected_message(self, sid, data):
#         """Demo message event for socket.io namespaces with guards."""
#         logger.info(f"Received message from client {sid}: {data}")
#         await socketio_server.emit(
#             "message", f"Protected message received from client: {data}"
#         )
