import functools
import inspect

from typing import Callable, Awaitable, Any, Sequence, Optional
from starlette.types import ASGIApp
from starlette.routing import BaseRoute, compile_path, Router  # Basically this file!
from starlette.middleware import Middleware

from dependencies.starlette_with_socketio.socketio import SocketIO


def socketio_session(
    func: Callable[[SocketIO], Awaitable[None]],
) -> ASGIApp:
    """
    Takes a coroutine `func(session)`, and returns an ASGI application.
    """
    # assert asyncio.iscoroutinefunction(func), "SocketIO endpoints must be async"


class SocketIORoute(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        namespace: Optional[str] = None,
        room: Optional[str] = None,
        middleware: Sequence[Middleware] | None = None,
    ) -> None:
        assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint
        self.namespace = namespace
        self.room = room

        endpoint_handler = endpoint
        while isinstance(endpoint_handler, functools.partial):
            endpoint_handler = endpoint_handler.func
        if inspect.isfunction(endpoint_handler) or inspect.ismethod(endpoint_handler):
            # Endpoint is function or method. Treat it as `func(socketio)`.
            self.app = socketio_session(endpoint)
        else:
            # Endpoint is a class. Treat it as ASGI.
            self.app = endpoint

        if middleware is not None:
            for cls, args, kwargs in reversed(middleware):
                self.app = cls(app=self.app, *args, **kwargs)

        self.path_regex, self.path_format, self.param_convertors = compile_path(path)


class RouterwithSocketIO(Router):
    def add_socketio_route(
        self,
        path: str,
        endpoint: Callable[[SocketIO], Awaitable[None]],
        namespace: Optional[str] = None,
        room: Optional[str] = None,
    ) -> None:
        route = SocketIORoute(path, endpoint=endpoint, namespace=namespace, room=room)
        self.routes.append(route)
