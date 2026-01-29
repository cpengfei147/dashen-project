"""
API路由定义
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from src.models.database import get_db
from src.models.schemas import (
    ChatRequest, ChatResponse, OrderResponse, OrderConfirmRequest
)
from src.agent.core import MovingAgent
from src.services.quote import QuoteService
from src.services.order import OrderService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: DBSession = Depends(get_db)):
    """发送消息"""
    # 获取或生成session_id
    session_id = request.session_id or str(uuid.uuid4())

    # 创建Agent实例
    agent = MovingAgent(db)

    # 处理消息
    response = await agent.chat(session_id, request.message)

    # 如果可以报价，计算报价
    quote = None
    if response.can_quote:
        quote_service = QuoteService()
        collected_data = agent.get_session_data(session_id)["collected_data"]
        quote = quote_service.calculate(collected_data)

    return ChatResponse(
        session_id=session_id,
        reply=response.reply,
        stage=response.stage,
        can_quote=response.can_quote,
        quote=quote,
        collected_data=agent.get_session_data(session_id)["collected_data"]
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: DBSession = Depends(get_db)):
    """获取会话信息"""
    agent = MovingAgent(db)
    session_data = agent.get_session_data(session_id)

    if not session_data["messages"]:
        raise HTTPException(status_code=404, detail="Session not found")

    return session_data


@router.post("/sessions/{session_id}/quote")
async def get_quote(session_id: str, db: DBSession = Depends(get_db)):
    """获取报价"""
    agent = MovingAgent(db)
    session_data = agent.get_session_data(session_id)

    if not session_data["messages"]:
        raise HTTPException(status_code=404, detail="Session not found")

    quote_service = QuoteService()
    quote = quote_service.calculate(session_data["collected_data"])

    return quote


@router.post("/sessions/{session_id}/order", response_model=OrderResponse)
async def create_order(session_id: str, db: DBSession = Depends(get_db)):
    """创建订单"""
    agent = MovingAgent(db)
    session_data = agent.get_session_data(session_id)

    if not session_data["messages"]:
        raise HTTPException(status_code=404, detail="Session not found")

    collected_data = session_data["collected_data"]

    # 检查必填信息
    required = ["address_from", "address_to", "moving_date"]
    missing = [f for f in required if not collected_data.get(f)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing)}"
        )

    # 计算报价
    quote_service = QuoteService()
    quote = quote_service.calculate(collected_data)

    # 创建订单
    order_service = OrderService(db)
    order = order_service.create_order(
        session_id=session_id,
        data=collected_data,
        quote_amount=quote["total"]
    )

    return OrderResponse(
        id=order.id,
        session_id=order.session_id,
        address_from=order.address_from,
        address_to=order.address_to,
        moving_date=order.moving_date,
        floor_from=order.floor_from,
        floor_to=order.floor_to,
        has_elevator_from=order.has_elevator_from,
        has_elevator_to=order.has_elevator_to,
        items_description=order.items_description,
        quote_amount=order.quote_amount,
        status=order.status,
        created_at=order.created_at.isoformat()
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: DBSession = Depends(get_db)):
    """获取订单"""
    order_service = OrderService(db)
    order = order_service.get_order(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        id=order.id,
        session_id=order.session_id,
        address_from=order.address_from,
        address_to=order.address_to,
        moving_date=order.moving_date,
        floor_from=order.floor_from,
        floor_to=order.floor_to,
        has_elevator_from=order.has_elevator_from,
        has_elevator_to=order.has_elevator_to,
        items_description=order.items_description,
        quote_amount=order.quote_amount,
        status=order.status,
        created_at=order.created_at.isoformat()
    )


@router.post("/orders/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: str,
    request: OrderConfirmRequest,
    db: DBSession = Depends(get_db)
):
    """确认订单"""
    order_service = OrderService(db)

    if request.confirmed:
        order = order_service.confirm_order(order_id)
    else:
        order = order_service.cancel_order(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        id=order.id,
        session_id=order.session_id,
        address_from=order.address_from,
        address_to=order.address_to,
        moving_date=order.moving_date,
        floor_from=order.floor_from,
        floor_to=order.floor_to,
        has_elevator_from=order.has_elevator_from,
        has_elevator_to=order.has_elevator_to,
        items_description=order.items_description,
        quote_amount=order.quote_amount,
        status=order.status,
        created_at=order.created_at.isoformat()
    )
