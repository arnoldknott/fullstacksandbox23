# import logging

# # from .sockets import socketio_server

# logger = logging.getLogger(__name__)


# # @sio.event
# # async def demo_message(sid, data):
# #     """Demo message event for socket.io."""
# #     print("=== demo_events - demo_message ===", flush=True)
# #     logger.info(f"Received message from client {sid}: {data}")
# #     await sio.emit("message", f"Message received from client {sid}: {data}")

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


# socketio_server.register_namespace(ProtectedEvents())
