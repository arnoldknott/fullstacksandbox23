from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.types import DecoratedCallable
from fastapi import routing
from typing import Any, Callable, Optional, Sequence
from typing_extensions import Annotated, Doc


class FastAPIwithSocketIO(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_api_socketio_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        namespace: Optional[str] = None,
        room: Optional[str] = None,
        *,
        dependencies: Optional[Sequence[Depends]] = None,
    ) -> None:
        self.router.add_api_socketio_route(  # TBD: implement this!
            path=path,
            endpoint=endpoint,
            namespace=namespace,
            room=room,
            dependencies=dependencies,
        )

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
        ],
        room: Annotated[
            Optional[str],
            Doc(
                """
                Socket.io room.
                """
            ),
        ],
        *,
        dependencies: Annotated[
            Optional[Sequence[Depends]],
            Doc(
                """
                A list of dependencies (using `Depends()`) to be used for this
                WebSocket.

                Read more about it in the
                [FastAPI docs for Socket.IO](https://fastapi.tiangolo.com/advanced/socketio/).
                """
            ),
        ] = None,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """
        Decorator to add a Socket.IO route.

        Read more about it in the
        [FastAPI docs for Socket.IO](https://fastapi.tiangolo.com/advanced/socketio/).

        ```python
        from fastapi import FastAPI, WebSocket

        app = FastAPI()

        @socketio_server.event
        @app.socketio("/socket.io")
        async def socketio_endpoint(sid, data):
            await socketio_server.emit("message", data)
        ```
        """

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_socketio_route(
                path,
                func,
                namespace=namespace,
                room=room,
                dependencies=dependencies,
            )
            return func

        return decorator

    def socketio_route(
        self,
        path: str,
        namespace: Optional[str] = None,
        room: Optional[str] = None,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.router.add_api_socketio_route(
                path,
                func,
                namespace=namespace,
                room=room,
            )
            return func

        return decorator
