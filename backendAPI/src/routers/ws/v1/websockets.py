import logging

from fastapi import APIRouter, WebSocket

logger = logging.getLogger(__name__)
router = APIRouter()

public_web_socket_on = True


@router.websocket("/public_web_socket")
async def demo_websocket_endpoint(websocket: WebSocket):
    logger.info("=== ws - v1 - public_web_socket ===")
    await websocket.accept()
    try:
        while public_web_socket_on:
            logger.info("=== ws - v1 - public_web_socket - connected ===")
            data = await websocket.receive_text()
            # TBD: the print's are no shown life in the console
            print("=== ws - v1 - public_web_socket - data ===")
            print(data)
            await websocket.send_text(f"Message received from client: {data}")
    except Exception as e:
        logger.info("=== ws - v1 - public_web_socket - exception ===")
        print("=== Exception in websocket ===")
        print(str(e))
        # raise WebSocketException(code=1011, reason=f"Websocket closed: {str(e)}")
        # raise WebSocketException(
        #     code=status.WS_1011_INTERNAL_ERROR, reason=f"Websocket closed: {str(e)}"
        # )
    finally:
        logger.info("=== ws - v1 - public_web_socket - disconnected ===")
        print("=== Websocket closed ===")
        await websocket.close()
