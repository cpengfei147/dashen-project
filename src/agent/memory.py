"""
简单会话记忆
"""
import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from src.models.database import Session as SessionModel


class SessionMemory:
    """会话记忆管理"""

    def __init__(self, db: DBSession):
        self.db = db

    def get_or_create_session(self, session_id: str) -> SessionModel:
        """获取或创建会话"""
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()

        if not session:
            session = SessionModel(
                id=session_id,
                messages=json.dumps([]),
                collected_data=json.dumps({}),
                stage="collecting",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

        return session

    def get_messages(self, session_id: str) -> list:
        """获取对话历史"""
        session = self.get_or_create_session(session_id)
        return json.loads(session.messages)

    def add_message(self, session_id: str, role: str, content: str):
        """添加消息"""
        session = self.get_or_create_session(session_id)
        messages = json.loads(session.messages)
        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages = json.dumps(messages, ensure_ascii=False)
        session.updated_at = datetime.utcnow()
        self.db.commit()

    def get_collected_data(self, session_id: str) -> dict:
        """获取已收集的信息"""
        session = self.get_or_create_session(session_id)
        return json.loads(session.collected_data)

    def update_collected_data(self, session_id: str, new_data: dict):
        """更新收集的信息（合并）"""
        session = self.get_or_create_session(session_id)
        current_data = json.loads(session.collected_data)

        # 合并新数据，只更新非null值
        for key, value in new_data.items():
            if value is not None:
                current_data[key] = value

        session.collected_data = json.dumps(current_data, ensure_ascii=False)
        session.updated_at = datetime.utcnow()
        self.db.commit()

    def get_stage(self, session_id: str) -> str:
        """获取当前阶段"""
        session = self.get_or_create_session(session_id)
        return session.stage

    def update_stage(self, session_id: str, stage: str):
        """更新阶段"""
        session = self.get_or_create_session(session_id)
        session.stage = stage
        session.updated_at = datetime.utcnow()
        self.db.commit()

    def clear_session(self, session_id: str):
        """清除会话"""
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        if session:
            self.db.delete(session)
            self.db.commit()
