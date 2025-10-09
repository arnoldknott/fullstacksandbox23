"""Socket.io version 1 hosts the socket.io endpoints for the first version of socket.io.
Note, socket.io is not compatible with websockets - it's using a different protocol.
Socket.io establishes the connection first vai HTTPS polling and then upgrades to websockets.
This module includes the tests for the endpoints:
in general each endpoint shall get its own tests."""

# Matches a BaseModel to a CRUD class:
# Format: <Model_class.__name__>: <namespace> as String
registry_namespaces = {}


def register_namespace(crud_instance, namespace):
    if (
        hasattr(crud_instance, "model")
        and crud_instance.model.__name__ not in registry_namespaces
    ):
        registry_namespaces[crud_instance.model.__name__] = namespace
