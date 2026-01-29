"""
主Agent实现
"""
import json
import re
from typing import Optional
from openai import OpenAI
from sqlalchemy.orm import Session as DBSession

from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from src.agent.prompts import SYSTEM_PROMPT
from src.agent.memory import SessionMemory
from src.models.schemas import AgentResponse, ExtractedInfo


class MovingAgent:
    """搬家助手Agent"""

    def __init__(self, db: DBSession):
        self.db = db
        self.memory = SessionMemory(db)
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )

    async def chat(self, session_id: str, message: str) -> AgentResponse:
        """处理用户消息"""
        # 1. 获取会话状态
        collected_data = self.memory.get_collected_data(session_id)
        stage = self.memory.get_stage(session_id)
        messages = self.memory.get_messages(session_id)

        # 2. 保存用户消息
        self.memory.add_message(session_id, "user", message)

        # 3. 构建系统prompt
        system_prompt = SYSTEM_PROMPT.format(
            collected_info=self._format_collected_info(collected_data),
            stage=stage
        )

        # 4. 构建消息列表
        llm_messages = [{"role": "system", "content": system_prompt}]

        # 添加历史消息（最近10轮）
        for msg in messages[-20:]:
            llm_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 添加当前用户消息
        llm_messages.append({"role": "user", "content": message})

        # 5. 调用LLM
        response = self._call_llm(llm_messages)

        # 6. 解析响应
        parsed = self._parse_response(response)

        # 7. 更新会话状态
        if parsed.extracted_info:
            self.memory.update_collected_data(
                session_id,
                parsed.extracted_info.model_dump(exclude_none=True)
            )

        if parsed.stage:
            self.memory.update_stage(session_id, parsed.stage)

        # 8. 保存助手回复
        self.memory.add_message(session_id, "assistant", parsed.reply)

        # 9. 检查是否可以报价
        updated_data = self.memory.get_collected_data(session_id)
        if self._is_info_complete(updated_data) and parsed.stage == "collecting":
            parsed.stage = "quoting"
            parsed.can_quote = True
            self.memory.update_stage(session_id, "quoting")

        return parsed

    def _format_collected_info(self, data: dict) -> str:
        """格式化已收集的信息"""
        if not data:
            return "暂无"

        info_map = {
            "address_from": "搬出地址",
            "address_to": "搬入地址",
            "moving_date": "搬家日期",
            "floor_from": "搬出楼层",
            "floor_to": "搬入楼层",
            "has_elevator_from": "搬出有电梯",
            "has_elevator_to": "搬入有电梯",
            "items_description": "物品描述"
        }

        lines = []
        for key, label in info_map.items():
            if key in data and data[key] is not None:
                value = data[key]
                if isinstance(value, bool):
                    value = "是" if value else "否"
                lines.append(f"- {label}: {value}")

        return "\n".join(lines) if lines else "暂无"

    def _call_llm(self, messages: list) -> str:
        """调用DeepSeek API"""
        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            # 返回错误时的兜底响应
            return json.dumps({
                "reply": "抱歉，我遇到了一点问题，请稍后再试。",
                "extracted_info": {},
                "stage": "collecting"
            }, ensure_ascii=False)

    def _parse_response(self, response: str) -> AgentResponse:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())

                extracted_info = None
                if "extracted_info" in data and data["extracted_info"]:
                    extracted_info = ExtractedInfo(**data["extracted_info"])

                return AgentResponse(
                    reply=data.get("reply", response),
                    extracted_info=extracted_info,
                    stage=data.get("stage", "collecting"),
                    can_quote=False
                )
        except (json.JSONDecodeError, Exception):
            pass

        # 解析失败，返回原始响应
        return AgentResponse(
            reply=response,
            extracted_info=None,
            stage="collecting",
            can_quote=False
        )

    def _is_info_complete(self, data: dict) -> bool:
        """检查必填信息是否完整"""
        required_fields = ["address_from", "address_to", "moving_date"]
        return all(
            field in data and data[field] is not None
            for field in required_fields
        )

    def get_session_data(self, session_id: str) -> dict:
        """获取会话数据"""
        return {
            "collected_data": self.memory.get_collected_data(session_id),
            "stage": self.memory.get_stage(session_id),
            "messages": self.memory.get_messages(session_id)
        }
