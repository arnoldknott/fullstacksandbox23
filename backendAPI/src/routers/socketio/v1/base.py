import logging
from pprint import pprint

import socketio

logger = logging.getLogger(__name__)

socketio_server = socketio.AsyncServer(
    async_mode="asgi", logger=True, engineio_logger=True
)

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
async def demo_message(sid, data):
    """Demo message event for socket.io."""
    print("=== demo_events - demo_message ===", flush=True)
    logger.info(f"Received message from client {sid}: {data}")
    await socketio_server.emit("demo_message", f"Message received from client: {data}")


@socketio_server.event(namespace="/protected_events")
async def protected_message(sid, data):
    """Protected message event for socket.io."""
    logger.info(f"Received protected message from client {sid}: {data}")
    await socketio_server.emit(
        "protected_message",
        f"Protected message received from client: {data}",
        namespace="/protected_events",
    )


# @socketio_server.event(namespace="/protected_events")
# async def protected_message(sid, data):
#     """Protected message event for socket.io."""
#     logger.info(f"Received protected message from client {sid}: {data}")
#     print("=== routers - socketio - v1 - protected_message - sid ===", flush=True)
#     print(sid, flush=True)
#     print("=== routers - socketio - v1 - protected_message - data ===", flush=True)
#     print(data, flush=True)
#     await socketio_server.emit(
#         "protected_message",
#         f"Protected message received from client: {data}",
#         namespace="/protected_events",
#     )


# class BaseEvents(socketio.AsyncNamespace):
#     """Base class for socket.io namespaces."""

#     def __init__(self, namespace: str = None, guards: GuardTypes = None, crud=None):
#         super().__init__(namespace=namespace)
#         self.guards = guards
#         self.crud = crud

#     async def on_connect(
#         self,
#         sid,
#         environ,
#         auth,
#         guards,
#         token_payload=Depends(get_access_token_payload),
#     ):
#         """Connect event for socket.io namespaces."""
#         guards = self.guards
#         print("=== base - on_connect - sid - environ ===")
#         print(environ, flush=True)
#         print("=== base - on_connect - sid - auth ===")
#         print(auth, flush=True)
#         print("=== base - on_connect - sid - guards ===")
#         print(guards, flush=True)
#         logger.info(f"Client connected with session id: {sid}.")
#         current_user = await check_token_against_guards(token_payload, self.guards)
#         print("=== base - on_connect - sid - current_user ===")
#         print(current_user, flush=True)
#         await socketio_server.emit("message", f"Hello new client with session id {sid}")

#     async def on_disconnect(self, sid):
#         """Disconnect event for socket.io namespaces."""
#         logger.info(f"Client with session id {sid} disconnected.")


# delete?:
# async def on_demo_message(self, sid, data):
#     """Demo message event for socket.io namespaces."""
#     logger.info(f"Received message from client {sid}: {data}")
#     await socketio_server.emit("message", f"Message received from client: {data}")

# async def on_demo_message_with_guards(self, sid, data):
#     """Demo message event for socket.io namespaces with guards."""
#     logger.info(f"Received message from client {sid}: {data}")
#     await check_token_against_guards(sid, data, self.guards)
#     await socketio_server.emit("message", f"Message received from client: {data}")
