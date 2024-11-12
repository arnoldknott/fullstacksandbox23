import enum

from starlette.requests import HTTPConnection
from starlette.types import Receive, Scope, Send


class SocketIOState(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTING = 2
    DISCONNECTED = 3


class SocketIO(HTTPConnection):

    def __init__(self, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope)
        self._receive = receive
        self._send = send
        self.client_state = SocketIOState.CONNECTING
        self.application_state = SocketIOState.CONNECTING

    # TBD: implement ASGI protocol methods from Socket.IO
