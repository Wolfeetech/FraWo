"""WebSocket connection manager for real-time updates."""

import json
from typing import Dict, List, Set

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.

    Supports room-based broadcasting for multi-station architecture.
    """

    def __init__(self) -> None:
        """Initialize connection manager."""
        # room_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> room_id mapping for quick lookup
        self.connection_rooms: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, room: str) -> None:
        """
        Accept and register a WebSocket connection to a room.

        Args:
            websocket: WebSocket connection
            room: Room identifier (e.g., station ID)
        """
        await websocket.accept()

        if room not in self.active_connections:
            self.active_connections[room] = set()

        self.active_connections[room].add(websocket)
        self.connection_rooms[websocket] = room

        logger.info(
            "websocket_connected",
            room=room,
            total_connections=len(self.active_connections[room]),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        room = self.connection_rooms.get(websocket)
        if room and room in self.active_connections:
            self.active_connections[room].discard(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

            logger.info(
                "websocket_disconnected",
                room=room,
                remaining_connections=len(self.active_connections.get(room, set())),
            )

        if websocket in self.connection_rooms:
            del self.connection_rooms[websocket]

    async def send_personal_message(self, message: str | dict, websocket: WebSocket) -> None:
        """
        Send a message to a specific WebSocket connection.

        Args:
            message: Message to send (string or dict for JSON)
            websocket: Target WebSocket connection
        """
        if websocket.client_state != WebSocketState.CONNECTED:
            return

        try:
            if isinstance(message, dict):
                await websocket.send_json(message)
            else:
                await websocket.send_text(message)
        except Exception as e:
            logger.error("failed_to_send_personal_message", error=str(e))
            self.disconnect(websocket)

    async def broadcast_to_room(self, message: str | dict, room: str) -> None:
        """
        Broadcast a message to all connections in a room.

        Args:
            message: Message to broadcast (string or dict for JSON)
            room: Room identifier
        """
        if room not in self.active_connections:
            return

        # Create list copy to avoid modification during iteration
        connections = list(self.active_connections[room])
        disconnected: List[WebSocket] = []

        for connection in connections:
            if connection.client_state != WebSocketState.CONNECTED:
                disconnected.append(connection)
                continue

            try:
                if isinstance(message, dict):
                    await connection.send_json(message)
                else:
                    await connection.send_text(message)
            except Exception as e:
                logger.error(
                    "failed_to_broadcast_to_connection",
                    room=room,
                    error=str(e),
                )
                disconnected.append(connection)

        # Clean up disconnected connections
        for ws in disconnected:
            self.disconnect(ws)

        logger.debug(
            "broadcast_complete",
            room=room,
            connections=len(connections) - len(disconnected),
            failed=len(disconnected),
        )

    async def broadcast_to_all(self, message: str | dict) -> None:
        """
        Broadcast a message to all active connections across all rooms.

        Args:
            message: Message to broadcast
        """
        for room in list(self.active_connections.keys()):
            await self.broadcast_to_room(message, room)

    def get_room_count(self, room: str) -> int:
        """
        Get the number of active connections in a room.

        Args:
            room: Room identifier

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(room, set()))

    def get_total_connections(self) -> int:
        """
        Get the total number of active connections.

        Returns:
            Total number of connections across all rooms
        """
        return sum(len(conns) for conns in self.active_connections.values())

    def get_rooms(self) -> List[str]:
        """
        Get list of active rooms.

        Returns:
            List of room identifiers
        """
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()
