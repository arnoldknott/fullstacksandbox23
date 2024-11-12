"""Socket.io version 1 hosts the socket.io endpoints for the first version of socket.io.
Note, socket.io is not compatible with websockets - it's using a different protocol.
Socket.io establishes the connection first vai HTTPS polling and then upgrades to websockets.
This module includes the tests for the endpoints:
in general each endpoint shall get its own tests."""
