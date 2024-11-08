import logging
from pprint import pprint
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()

public_web_socket_on = True
clients: List[WebSocket] = []


@router.websocket("/public_web_socket")
async def demo_websocket_endpoint(websocket: WebSocket):
    logger.info("=== ws - v1 - public_web_socket ===")
    await websocket.accept()
    clients.append(websocket)
    print("=== ws - v1 - public_web_socket - connected ===")
    print("=== clients ===")
    pprint([vars(client) for client in clients])
    print("=== websocket ===")
    pprint(vars(websocket))
    try:
        while public_web_socket_on:
            logger.info("=== ws - v1 - public_web_socket - connected ===")
            data = await websocket.receive_text()
            # TBD: the print's are not shown life in the console
            print("=== ws - v1 - public_web_socket - data ===", flush=True)
            print(data, flush=True)
            # await websocket.send_text(f"Message received from client: {data}")
            for client in clients:
                await client.send_text(f"Message received from client: {data}")
    except WebSocketDisconnect:
        logger.info("=== ws - v1 - public_web_socket - disconnected ===")
        print("=== Websocket closed ===", flush=True)
        print("=== websocket ===", flush=True)
        print(websocket, flush=True)
        clients.remove(websocket)
    except Exception as e:
        logger.info("=== ws - v1 - public_web_socket - exception ===")
        print("=== Exception in websocket ===", flush=True)
        print(str(e), flush=True)
        # raise WebSocketException(code=1011, reason=f"Websocket closed: {str(e)}")
        # raise WebSocketException(
        #     code=status.WS_1011_INTERNAL_ERROR, reason=f"Websocket closed: {str(e)}"
        # )
    finally:
        if websocket in clients:
            clients.remove(websocket)
        logger.info("=== ws - v1 - public_web_socket - disconnected ===")
        print("=== Websocket closed ===")
        try:
            await websocket.close()
        except Exception as e:
            logger.info("=== ws - v1 - public_web_socket - exception ===")
            print("=== Exception in closing websocket ===", flush=True)
            print(str(e), flush=True)
