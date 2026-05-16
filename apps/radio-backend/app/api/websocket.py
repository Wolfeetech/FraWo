"""WebSocket API endpoints for real-time updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.services.websocket import manager

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/{station_id}")
async def websocket_endpoint(websocket: WebSocket, station_id: int) -> None:
    """
    WebSocket endpoint for real-time station updates.

    Connect to receive live updates about:
    - Now playing information
    - Listener count changes
    - Station status changes

    **Connection**: `ws://host:port/api/ws/{station_id}`

    **Messages** are sent as JSON:
    ```json
    {
        "type": "now_playing",
        "data": {
            "artist": "Artist Name",
            "title": "Track Title",
            "album": "Album Name",
            "listeners": 42
        }
    }
    ```
    """
    room = f"station_{station_id}"

    await manager.connect(websocket, room)
    logger.info("websocket_client_connected", station_id=station_id, room=room)

    try:
        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "welcome",
                "message": f"Connected to station {station_id}",
                "station_id": station_id,
            },
            websocket,
        )

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()
            logger.debug("websocket_message_received", station_id=station_id, data=data)

            # Echo back for now (can be extended with commands)
            await manager.send_personal_message(
                {"type": "echo", "data": data},
                websocket,
            )

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", station_id=station_id, room=room)
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", station_id=station_id, error=str(e))
        manager.disconnect(websocket)


@router.get(
    "/stats",
    summary="Get WebSocket statistics",
    description="Get current WebSocket connection statistics",
)
async def get_websocket_stats() -> JSONResponse:
    """
    Get WebSocket connection statistics.

    Returns information about active connections and rooms.
    """
    stats = {
        "total_connections": manager.get_total_connections(),
        "active_rooms": manager.get_rooms(),
        "room_details": {room: manager.get_room_count(room) for room in manager.get_rooms()},
    }

    logger.debug("websocket_stats_requested", stats=stats)
    return JSONResponse(content=stats)
