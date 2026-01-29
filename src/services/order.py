"""
订单服务
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from src.models.database import Order


class OrderService:
    """订单服务"""

    def __init__(self, db: DBSession):
        self.db = db

    def create_order(self, session_id: str, data: dict, quote_amount: float) -> Order:
        """创建订单"""
        order = Order(
            id=str(uuid.uuid4()),
            session_id=session_id,
            address_from=data.get("address_from"),
            address_to=data.get("address_to"),
            moving_date=data.get("moving_date"),
            floor_from=data.get("floor_from"),
            floor_to=data.get("floor_to"),
            has_elevator_from=data.get("has_elevator_from"),
            has_elevator_to=data.get("has_elevator_to"),
            items_description=data.get("items_description"),
            quote_amount=quote_amount,
            status="pending",
            created_at=datetime.utcnow()
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_order_by_session(self, session_id: str) -> Optional[Order]:
        """通过会话ID获取订单"""
        return self.db.query(Order).filter(
            Order.session_id == session_id
        ).order_by(Order.created_at.desc()).first()

    def confirm_order(self, order_id: str) -> Optional[Order]:
        """确认订单"""
        order = self.get_order(order_id)
        if order:
            order.status = "confirmed"
            self.db.commit()
            self.db.refresh(order)
        return order

    def cancel_order(self, order_id: str) -> Optional[Order]:
        """取消订单"""
        order = self.get_order(order_id)
        if order:
            order.status = "cancelled"
            self.db.commit()
            self.db.refresh(order)
        return order

    def list_orders(self, skip: int = 0, limit: int = 20) -> list:
        """获取订单列表"""
        return self.db.query(Order).order_by(
            Order.created_at.desc()
        ).offset(skip).limit(limit).all()
