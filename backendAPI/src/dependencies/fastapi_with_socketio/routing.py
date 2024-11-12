from contextlib import AsyncExitStack
from typing import Any, Callable, Coroutine, Optional, Sequence, Tuple

from typing_extensions import Annotated, Doc

from fastapi import params
from fastapi._compat import _normalize_errors
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    solve_dependencies,
    get_dependant,
    get_parameterless_sub_dependant,
    get_flat_dependant,
    _should_embed_body_fields,
)
from fastapi.types import DecoratedCallable
from dependencies.fastapi_with_socketio.exceptions import SocketIORequestValidationError
from fastapi.routing import APIRouter  # basically this file!

from starlette.routing import compile_path, Match
from starlette.types import Scope
from dependencies.starlette_with_socketio.socketio import (
    SocketIO,
)  # TBD: implement ASGI protocol for Socket.IO
from dependencies.starlette_with_socketio.routing import (
    socketio_session,
    SocketIORoute,
    RouterwithSocketIO,
)


def get_socketio_app(
    dependant: Dependant,
    dependency_overrides_provider: Optional[Any] = None,
    embed_body_fields: bool = False,
) -> Callable[[SocketIO], Coroutine[Any, Any, Any]]:
    async def app(socketio: SocketIO) -> None:
        async with AsyncExitStack() as async_exit_stack:
            solved_result = await solve_dependencies(
                request=socketio,
                dependant=dependant,
                dependency_overrides_provider=dependency_overrides_provider,
                async_exit_stack=async_exit_stack,
                embed_body_fields=embed_body_fields,
            )
            if solved_result.errors:
                raise SocketIORequestValidationError(
                    _normalize_errors(solved_result.errors)
                )
            assert dependant.call is not None, "dependant.call must be a function"
            await dependant.call(**solved_result.values)


class APISocketIORoute(SocketIORoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        namespace: Optional[str] = None,
        room: Optional[str] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        dependency_overrides_provider: Optional[Any] = None,
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.namespace = namespace
        self.room = room
        self.dependencies = list(dependencies or [])
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)
        self.dependant = get_dependant(path=self.path_format, call=self.endpoint)
        for depends in self.dependencies[::-1]:
            self.dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(depends=depends, path=self.path_format),
            )
        self._flat_dependant = get_flat_dependant(self.dependant)
        self._embed_body_fields = _should_embed_body_fields(
            self._flat_dependant.body_params
        )
        self.app = socketio_session(
            get_socketio_app(
                dependant=self.dependant,
                dependency_overrides_provider=dependency_overrides_provider,
                embed_body_fields=self._embed_body_fields,
            )
        )

    def matches(self, scope: Scope) -> Tuple[Match, Scope]:
        match, child_scope = super().matches(scope)
        if match != Match.NONE:
            child_scope["route"] = self
        return match, child_scope


class APIRouterWithSocketIO(APIRouter, RouterwithSocketIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_api_socketio_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        namespace: Optional[str] = None,
        room: Optional[str] = None,
        *,
        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> None:
        current_dependencies = self.dependencies.copy()
        if dependencies:
            current_dependencies.extend(dependencies)

        route = APISocketIORoute(
            self.prefix + path,
            endpoint=endpoint,
            namespace=namespace,
            room=room,
            dependencies=current_dependencies,
            dependency_overrides_provider=self.dependency_overrides_provider,
        )
        self.routes.append(route)

    def socketio(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Socket.io path.
                """
            ),
        ],
        namespace: Annotated[
            Optional[str],
            Doc(
                """
                Socket.io namespace.
                """
            ),
        ] = None,
        room: Annotated[
            Optional[str],
            Doc(
                """
                Socket.io room.
                """
            ),
        ] = None,
        *,
        dependencies: Annotated[
            Optional[Sequence[params.Depends]],
            Doc(
                """
                A list of dependencies (using `Depends()`) to be used for this Socket.IO.

                Read more about it in the
                [FastAPI docs for WebSockets](https://fastapi.tiangolo.com/advanced/socketio/).
                """
            ),
        ] = None,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """
        Decorate a SocketIO function.

        Read more about it in the
        [FastAPI docs for WebSockets](https://fastapi.tiangolo.com/advanced/socketio/).

        **Example**

        ## Example

        ```python
        from fastapi import APIRouter, FastAPI, WebSocket

        app = FastAPI()
        router = APIRouter()

        @router.socketio("/socket.io")
        async def socketio_endpoint(sid, data):
            await socketio_server.emit("message", data)

        app.include_router(router)
        ```
        """

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_socketio_route(
                path, func, namespace=namespace, room=room, dependencies=dependencies
            )
            return func

        return decorator

    def socketio_route(
        self, path: str, namespace: Optional[str] = None, room: Optional[str] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_socketio_route(path, func, namespace=namespace, room=room)
            return func

        return decorator
