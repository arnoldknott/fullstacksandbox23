import logging

from fastapi import APIRouter, WebSocket, WebSocketException

logger = logging.getLogger(__name__)
router = APIRouter()

public_web_socket_on = True


@router.websocket("/public_web_socket")
async def demo_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while public_web_socket_on:
            data = await websocket.receive_text()
            # print("=== ws - v1 - public_web_socket - data ===")
            # print(data)
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        await websocket.close()
        raise WebSocketException(code=1011, detail=f"Websocket closed: {str(e)}")
