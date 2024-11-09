import logging

import socketio

logger = logging.getLogger(__name__)

socketio_server = socketio.AsyncServer(async_mode="asgi")
socketio_app = socketio.ASGIApp(socketio_server, socketio_path="socketio/v1")
# print("=== core - sockets - vars(socketio_server) ===")
# pprint(vars(socketio_server))
# print("=== core - sockets - dir(socketio_server) ===")
# pprint(dir(socketio_server))
# print("=== core - sockets - var(socketio_app) ===")
# pprint(socketio_app)
# print("=== core - sockets - dir(socketio_app) ===")
# pprint(dir(socketio_app))
# print("=== core - sockets - flush ===", flush=True)


# TBD: add auth as FastAPI Depends
@socketio_server.event
async def connect(sid, environ, auth):
    """Connect event for socket.io."""
    logger.info(f"Client connected with session id: {sid}.")
    print("=== core - sockets - connect - sid ===")
    print(sid)
    print("=== core - sockets - environ ===")
    print(environ)
    print("=== core - sockets - environ ===")
    print(auth)
    await socketio_server.emit("message", f"Hello new client with session id {sid}")
    # TBD: add rooms and namespaces?
    # TBD: or refuse connection
    # for example if authentication is not successful:
    # raise ConnectionRefusedError("Connection refused")


@socketio_server.event
async def disconnect(sid):
    """Disconnect event for socket.io."""
    logger.info(f"Client with session id {sid} disconnected.")
    print("=== core - sockets - disconnect - sid ===")
    print(sid)


@socketio_server.on("*")
async def catch_all(sid, data):
    """Catch all events for socket.io, that don't have an event handler defined."""
    logger.info(f"Caught event {data} from client {sid}.")
    print("=== core - sockets - catch_all - sid ===")
    print(sid)
    print("=== core - sockets - catch_all - data ===")
    print(data)


@socketio_server.event
async def demo_message(sid, data):
    """Demo message event for socket.io."""
    print("=== demo_events - demo_message ===", flush=True)
    logger.info(f"Received message from client {sid}: {data}")
    await socketio_server.emit("message", f"Message received from client: {data}")
