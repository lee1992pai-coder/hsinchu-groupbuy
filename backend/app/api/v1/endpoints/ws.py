"""
WebSocket：商家即時接單通知
連線方式：ws://host/ws/merchant/{merchant_id}
"""
import asyncio
import json
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.order import Order, OrderStatus

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = logging.getLogger(__name__)

# merchant_id → set of WebSocket connections
_connections: dict[str, set[WebSocket]] = {}


@router.websocket("/merchant/{merchant_id}")
async def merchant_ws(websocket: WebSocket, merchant_id: str):
    await websocket.accept()
    _connections.setdefault(merchant_id, set()).add(websocket)
    logger.info("Merchant %s connected (ws)", merchant_id)
    try:
        while True:
            # 每 30 秒 ping 一次保持連線
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        _connections[merchant_id].discard(websocket)
        logger.info("Merchant %s disconnected (ws)", merchant_id)


async def notify_merchant_new_order(merchant_id: str, order_data: dict):
    """從其他地方呼叫，通知商家新訂單"""
    sockets = _connections.get(merchant_id, set()).copy()
    for ws in sockets:
        try:
            await ws.send_json({"type": "new_order", "order": order_data})
        except Exception:
            _connections[merchant_id].discard(ws)
