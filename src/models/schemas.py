"""
Pydantic数据模型
"""
from typing import Optional, List
from pydantic import BaseModel


class ExtractedInfo(BaseModel):
    """从对话中提取的信息"""
    address_from: Optional[str] = None
    address_to: Optional[str] = None
    moving_date: Optional[str] = None
    floor_from: Optional[int] = None
    floor_to: Optional[int] = None
    has_elevator_from: Optional[bool] = None
    has_elevator_to: Optional[bool] = None
    items_description: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent响应"""
    reply: str
    extracted_info: Optional[ExtractedInfo] = None
    stage: str = "collecting"
    can_quote: bool = False
    quote: Optional[dict] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    reply: str
    stage: str
    can_quote: bool = False
    quote: Optional[dict] = None
    collected_data: Optional[dict] = None


class QuoteDetail(BaseModel):
    """报价明细"""
    item: str
    amount: float
    description: Optional[str] = None


class QuoteResponse(BaseModel):
    """报价响应"""
    total: float
    details: List[QuoteDetail]
    currency: str = "CNY"
    valid_until: str


class OrderResponse(BaseModel):
    """订单响应"""
    id: str
    session_id: str
    address_from: str
    address_to: str
    moving_date: str
    floor_from: Optional[int] = None
    floor_to: Optional[int] = None
    has_elevator_from: Optional[bool] = None
    has_elevator_to: Optional[bool] = None
    items_description: Optional[str] = None
    quote_amount: float
    status: str
    created_at: str


class OrderConfirmRequest(BaseModel):
    """订单确认请求"""
    confirmed: bool = True
