"""
SQLite数据库模型
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, Boolean, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from src.config import DATABASE_URL, BASE_DIR

Base = declarative_base()


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    messages = Column(Text, default="[]")  # JSON存储对话历史
    collected_data = Column(Text, default="{}")  # JSON存储已收集信息
    stage = Column(String(20), default="collecting")  # 当前阶段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), index=True)
    address_from = Column(Text)
    address_to = Column(Text)
    moving_date = Column(String(20))
    floor_from = Column(Integer, nullable=True)
    floor_to = Column(Integer, nullable=True)
    has_elevator_from = Column(Boolean, nullable=True)
    has_elevator_to = Column(Boolean, nullable=True)
    items_description = Column(Text, nullable=True)
    quote_amount = Column(Float)
    status = Column(String(20), default="pending")  # pending/confirmed/cancelled/completed
    created_at = Column(DateTime, default=datetime.utcnow)


# 确保数据目录存在
data_dir = BASE_DIR / "data"
data_dir.mkdir(exist_ok=True)

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库（创建表）"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话（依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
