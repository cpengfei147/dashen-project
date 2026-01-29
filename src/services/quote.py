"""
报价计算服务
"""
from datetime import datetime
from typing import Optional

# 报价规则
PRICING = {
    "base_price": 300,           # 基础价格
    "cross_district_extra": 100, # 跨区加价
    "floor_no_elevator": 50,     # 无电梯每层加价
    "weekend_multiplier": 1.1,   # 周末加价系数
    "large_items_extra": 100,    # 大件物品加价
}


class QuoteService:
    """报价计算服务"""

    def calculate(self, data: dict) -> dict:
        """计算报价"""
        details = []
        total = PRICING["base_price"]
        details.append({
            "item": "基础服务费",
            "amount": PRICING["base_price"],
            "description": "包含基础搬运服务"
        })

        # 楼层加价（搬出）
        floor_from = data.get("floor_from")
        has_elevator_from = data.get("has_elevator_from")
        if floor_from and not has_elevator_from:
            floor_charge = (floor_from - 1) * PRICING["floor_no_elevator"]
            if floor_charge > 0:
                total += floor_charge
                details.append({
                    "item": "搬出楼层费",
                    "amount": floor_charge,
                    "description": f"{floor_from}楼无电梯"
                })

        # 楼层加价（搬入）
        floor_to = data.get("floor_to")
        has_elevator_to = data.get("has_elevator_to")
        if floor_to and not has_elevator_to:
            floor_charge = (floor_to - 1) * PRICING["floor_no_elevator"]
            if floor_charge > 0:
                total += floor_charge
                details.append({
                    "item": "搬入楼层费",
                    "amount": floor_charge,
                    "description": f"{floor_to}楼无电梯"
                })

        # 周末加价
        moving_date = data.get("moving_date")
        if moving_date:
            try:
                date_obj = datetime.strptime(moving_date, "%Y-%m-%d")
                if date_obj.weekday() >= 5:  # 周六或周日
                    weekend_extra = int(total * (PRICING["weekend_multiplier"] - 1))
                    total += weekend_extra
                    details.append({
                        "item": "周末服务费",
                        "amount": weekend_extra,
                        "description": "周末搬家加价10%"
                    })
            except ValueError:
                pass

        # 大件物品
        items_desc = data.get("items_description", "")
        large_items = ["钢琴", "保险柜", "鱼缸", "大型家具"]
        if items_desc and any(item in items_desc for item in large_items):
            total += PRICING["large_items_extra"]
            details.append({
                "item": "大件物品费",
                "amount": PRICING["large_items_extra"],
                "description": "包含大件物品搬运"
            })

        return {
            "total": total,
            "details": details,
            "currency": "CNY",
            "valid_until": "报价有效期3天"
        }

    def format_quote(self, quote: dict) -> str:
        """格式化报价文本"""
        lines = ["【搬家报价】\n"]

        for detail in quote["details"]:
            lines.append(f"- {detail['item']}: ¥{detail['amount']}")
            if detail.get("description"):
                lines.append(f"  ({detail['description']})")

        lines.append(f"\n总计: ¥{quote['total']}")
        lines.append(f"\n{quote['valid_until']}")

        return "\n".join(lines)
