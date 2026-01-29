# 智能搬家助手技术架构设计文档

> 版本：V1.0
> 日期：2026-01-29
> 状态：待评审

---

## 目录

1. [项目概述](#第一部分项目概述)
2. [设计原则与架构总览](#第二部分设计原则与架构总览)
3. [核心组件详细设计](#第三部分核心组件详细设计)
4. [专家顾问系统设计](#第四部分专家顾问系统设计)
5. [生成层与工具箱设计](#第五部分生成层与工具箱设计)
6. [整体流程与技术选型](#第六部分整体流程与技术选型)
7. [数据库设计与API接口定义](#第七部分数据库设计与api接口定义)
8. [对话示例与测试用例](#第八部分对话示例与测试用例)
9. [风险与应对 + 总结](#第九部分风险与应对--总结)
10. [设计分析报告](#第十部分设计深度分析报告)

---

## 第一部分：项目概述

### 1.1 项目背景

现有搬家Agent存在的问题：
- 前端正则匹配 + 后端模板式提示词，本质是"伪AI"
- 没有上下文理解，用户换个说法就不认识
- 没有记忆系统，无法跨轮次/跨会话记住信息
- 没有RAG知识增强，无法回答专业问题
- 流程固化，像填表单而非自然对话
- 用户和老板评价："智障AI"

### 1.2 项目目标

参考蚂蚁阿福，重构搬家Agent，实现：
- **自然对话**：像和真人朋友聊天，不是填表
- **上下文理解**：理解用户意图，支持多种表达方式
- **记忆能力**：记住本次对话内容，未来支持跨会话记忆
- **知识增强**：能回答搬家相关专业问题
- **多模态**：支持图片识别（拍照估算物品量）
- **目标驱动**：主动推进对话，而非被动等待

### 1.3 核心设计理念

**"主Agent + 专家顾问"架构**

- 一个主Agent始终在场，保持人格统一和对话连贯
- 专家顾问提供专业支持，但不接管对话
- LLM始终是决策主体，避免回到规则驱动的死板模式

---

## 第二部分：设计原则与架构总览

### 2.1 设计原则

| 原则 | 说明 | 反面案例 |
|------|------|----------|
| **LLM决策主体** | 所有对话决策由LLM做出，规则只提供数据 | 规则判断意图→固定回复 |
| **单一对话主体** | 用户始终感觉在和一个人对话 | 多Agent切换，人格不一致 |
| **目标驱动** | Agent有自己的目标，主动推进对话 | 纯响应式，用户不说就不动 |
| **情绪优先** | 先处理情绪，再处理业务 | 用户说"烦死了"，回复"请问地址是？" |
| **对话式交互** | 每次只问1-2个问题，自然过渡 | 一次要求填5个字段 |
| **渐进式信息收集** | 用户主动给的就收，不机械追问 | "您还没告诉我日期" |
| **优雅降级** | 不确定时承认，必要时转人工 | 瞎编答案或死循环 |

### 2.2 架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              用户界面 (H5/Web)                           │
│                        文字输入 | 图片上传 | 订单展示                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ WebSocket / HTTP
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              API Gateway                                 │
│                        认证 | 限流 | 日志 | 路由                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                         主Agent服务（核心）                               │
│                                                                          │
│    ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐    │
│    │  理解层    │──▶│   记忆层   │──▶│   规划层   │──▶│  生成层    │    │
│    └────────────┘   └────────────┘   └────────────┘   └────────────┘    │
│           │                │                │                │           │
│           └────────────────┴────────────────┴────────────────┘           │
│                                     │                                    │
│                                     ▼                                    │
│    ┌────────────────────────────────────────────────────────────────┐   │
│    │                        专家顾问系统                             │   │
│    │     情感顾问 | 知识顾问(RAG) | 业务顾问 | 订单顾问               │   │
│    └────────────────────────────────────────────────────────────────┘   │
│                                     │                                    │
│                                     ▼                                    │
│    ┌────────────────────────────────────────────────────────────────┐   │
│    │                          工具箱                                 │   │
│    │   地址验证 | 报价计算 | 图片识别 | 库存查询 | 订单API            │   │
│    └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌────────────┐   ┌────────────┐   ┌────────────┐
            │  向量数据库 │   │  业务数据库 │   │  外部服务   │
            │ (知识/记忆) │   │ (订单/用户) │   │ (地图/支付) │
            └────────────┘   └────────────┘   └────────────┘
```

### 2.3 核心数据流

```
用户消息
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 理解层：解析用户输入                                       │
│    - 提取实体（地址、日期、物品）                              │
│    - 识别意图（可多个）                                       │
│    - 判断情感状态                                             │
│    - 分析对话行为                                             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 记忆层：加载上下文                                         │
│    - 读取工作记忆（当前焦点）                                  │
│    - 读取会话记忆（已收集信息）                                │
│    - 读取长期记忆（用户画像）                                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 规划层：决定行动策略                                       │
│    - 检查当前目标                                             │
│    - 判断是否需要咨询专家                                      │
│    - 确定回应策略（情感安抚/回答问题/收集信息/...）            │
└─────────────────────────────────────────────────────────────┘
    │
    ▼ (如需要)
┌─────────────────────────────────────────────────────────────┐
│ 4. 专家顾问：获取专业支持                                     │
│    - 情感顾问：情绪回应建议                                    │
│    - 知识顾问：RAG检索答案                                    │
│    - 业务顾问：报价计算、规则校验                              │
│    - 订单顾问：状态管理、字段校验                              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 生成层：综合生成回复                                       │
│    - 综合理解、记忆、规划、专家建议                            │
│    - 按人格特点（耐心、专业、温暖）生成自然回复                 │
│    - 更新记忆状态                                             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Agent回复
```

### 2.4 与原设计的对比

| 维度 | 原设计（Router+多Agent） | 新设计（主Agent+专家顾问） |
|------|-------------------------|--------------------------|
| 决策流程 | Router判断→分发到Agent→Agent独立回复 | 主Agent理解→咨询专家→主Agent综合回复 |
| 人格管理 | 各Agent独立，需后处理统一 | 天然统一，只有一个对话主体 |
| 意图处理 | 硬分类，一条消息一个意图 | 软解析，支持多意图融合 |
| 专家角色 | 独立Agent，全权处理 | 顾问角色，提供建议不接管 |
| 目标感 | 无，纯响应式 | 有，规划层维护目标栈 |
| 灵活性 | 受Router分类限制 | LLM自主决策，更灵活 |
| 延迟 | 2-3次LLM调用 | 简单情况1次，复杂情况2次 |

---

## 第三部分：核心组件详细设计

### 3.1 理解层（Understanding Layer）

#### 3.1.1 职责

将用户输入解析为结构化的多维度理解，供后续层使用。

**核心理念：不做硬分类，而是多维度软解析。**

#### 3.1.2 输入输出

```
输入：
  - user_message: string          # 用户消息文本
  - images: list[Image]           # 用户上传的图片（可选）
  - session_context: SessionContext  # 会话上下文

输出：
  - Understanding: 结构化理解结果
```

#### 3.1.3 理解结果数据结构

```typescript
interface Understanding {
  // 实体提取：用户消息中的关键信息
  entities: {
    address_from?: string;        // 搬出地址
    address_to?: string;          // 搬入地址
    date?: string;                // 搬家日期
    time_preference?: string;     // 时间偏好（上午/下午）
    items?: string[];             // 提到的物品
    floor_from?: number;          // 搬出楼层
    floor_to?: number;            // 搬入楼层
    has_elevator?: boolean;       // 是否有电梯
    special_requirements?: string; // 特殊需求
  };

  // 意图识别：用户想做什么（可多个，带置信度）
  intents: Array<{
    type: IntentType;
    confidence: number;           // 0-1
    details?: string;             // 补充说明
  }>;

  // 情感分析：用户的情绪状态
  emotion: {
    valence: 'positive' | 'neutral' | 'slightly_negative' | 'negative';
    arousal: 'low' | 'medium' | 'high';  // 情绪强度
    specific_emotions?: string[];         // 具体情绪（焦虑、着急、不满等）
    needs_attention: boolean;             // 是否需要优先处理情绪
    concerns?: string[];                  // 用户担心的点
  };

  // 对话行为：这句话在对话中的作用
  dialogue_act: DialogueAct;

  // 图片理解（如有图片）
  image_understanding?: {
    detected_items: Array<{
      category: string;           // 物品类别
      description: string;        // 描述
      estimated_volume?: string;  // 估算体积
    }>;
    room_type?: string;           // 房间类型
    overall_assessment: string;   // 整体评估
  };

  // 元信息
  meta: {
    is_greeting: boolean;         // 是否是打招呼
    is_farewell: boolean;         // 是否是告别
    is_confirmation: boolean;     // 是否是确认（"好的"、"对"）
    is_negation: boolean;         // 是否是否定（"不是"、"不对"）
    is_question: boolean;         // 是否在提问
    is_correction: boolean;       // 是否在纠正之前的信息
    requires_human: boolean;      // 是否需要转人工
  };
}

// 意图类型枚举
enum IntentType {
  // 信息类
  PROVIDE_INFO = 'provide_info',           // 提供信息
  ASK_QUESTION = 'ask_question',           // 询问问题
  REQUEST_QUOTE = 'request_quote',         // 请求报价

  // 操作类
  START_BOOKING = 'start_booking',         // 开始预约
  MODIFY_INFO = 'modify_info',             // 修改信息
  CANCEL = 'cancel',                       // 取消
  CONFIRM = 'confirm',                     // 确认

  // 情感类
  EXPRESS_EMOTION = 'express_emotion',     // 表达情绪
  SEEK_COMFORT = 'seek_comfort',           // 寻求安慰

  // 其他
  CHIT_CHAT = 'chit_chat',                 // 闲聊
  REQUEST_HUMAN = 'request_human',         // 要求转人工
  OTHER = 'other'
}

// 对话行为枚举
enum DialogueAct {
  INITIATE = 'initiate',                   // 发起对话
  RESPOND = 'respond',                     // 回应上一轮
  FOLLOW_UP = 'follow_up',                 // 追问
  CLARIFY = 'clarify',                     // 澄清
  CORRECT = 'correct',                     // 纠正
  CONFIRM = 'confirm',                     // 确认
  REJECT = 'reject',                       // 拒绝
  DIGRESS = 'digress',                     // 跑题
  CLOSE = 'close'                          // 结束
}
```

#### 3.1.4 实现方案

**方案：单次LLM调用 + 结构化输出**

```python
class UnderstandingLayer:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.vision_model = VisionModel()  # 图片识别

    async def parse(
        self,
        user_message: str,
        images: list = None,
        session_context: dict = None
    ) -> Understanding:

        # 如果有图片，先进行图片理解
        image_understanding = None
        if images:
            image_understanding = await self._understand_images(images)

        # 构建理解prompt
        prompt = self._build_understanding_prompt(
            user_message,
            session_context,
            image_understanding
        )

        # 调用LLM，要求JSON格式输出
        result = await self.llm.generate(
            prompt,
            response_format={"type": "json_object"}
        )

        return Understanding.parse(result)

    def _build_understanding_prompt(self, message, context, image_info):
        return f"""
你是一个对话理解专家。请分析用户的这条消息，提取多维度信息。

【对话上下文】
{self._format_context(context)}

【用户消息】
{message}

【图片信息】（如有）
{image_info or "无图片"}

请以JSON格式输出以下维度的分析：

1. entities: 提取消息中的实体信息（地址、日期、物品等）
2. intents: 识别用户意图（可多个，附带置信度0-1）
3. emotion: 分析情感状态和情绪强度
4. dialogue_act: 判断这句话在对话中的作用
5. meta: 元信息判断

注意：
- 意图可以有多个，按置信度排序
- 情感分析要考虑隐含情绪，不只是显式表达
- 如果信息不完整，对应字段留空，不要猜测

输出JSON：
"""

    async def _understand_images(self, images) -> dict:
        """图片理解：识别物品、估算体积"""
        results = []
        for img in images:
            analysis = await self.vision_model.analyze(
                img,
                prompt="识别图中的家具和物品，估算搬家体积"
            )
            results.append(analysis)

        return {
            "detected_items": results,
            "overall_assessment": self._summarize_items(results)
        }
```

#### 3.1.5 理解层的关键设计点

| 设计点 | 说明 |
|--------|------|
| 多意图支持 | 不强制单一意图，允许"提供信息+询问价格"同时存在 |
| 置信度 | 每个意图带置信度，供规划层决策 |
| 情绪优先标记 | `needs_attention`字段，触发情绪优先处理 |
| 纠正识别 | `is_correction`标记，区分"补充"和"修改" |
| 图片融合 | 图片理解结果融入整体Understanding |

---

### 3.2 记忆层（Memory Layer）

#### 3.2.1 职责

管理三层记忆系统，为Agent提供上下文支持。

#### 3.2.2 三层记忆架构

```
┌─────────────────────────────────────────────────────────────┐
│                    第一层：工作记忆                          │
│                  （当前对话焦点，最近几轮）                   │
│                     保留时间：当前会话                        │
│                     存储位置：内存/Redis                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    第二层：会话记忆                          │
│                （本次会话的摘要和收集到的数据）               │
│                     保留时间：会话结束后24小时                │
│                     存储位置：Redis/数据库                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    第三层：长期记忆                          │
│                    （用户画像，跨会话）                       │
│                     保留时间：永久                           │
│                     存储位置：数据库+向量库                   │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.3 数据结构

```typescript
// 工作记忆：当前对话焦点
interface WorkingMemory {
  session_id: string;

  // 最近对话轮次（保留最近5轮原文）
  recent_turns: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
    understanding?: Understanding;  // 用户消息的理解结果
  }>;

  // 当前焦点
  current_topic: string;            // 当前在聊什么
  pending_questions: string[];      // 待收集的信息
  last_agent_action: string;        // 上一步Agent做了什么

  // 即时状态
  user_current_emotion: string;     // 用户当前情绪
  conversation_stage: ConversationStage;  // 对话阶段
}

// 对话阶段
enum ConversationStage {
  GREETING = 'greeting',            // 打招呼
  UNDERSTANDING_NEED = 'understanding_need',  // 了解需求
  COLLECTING_BASIC = 'collecting_basic',      // 收集基本信息
  COLLECTING_DETAIL = 'collecting_detail',    // 收集详细信息
  QUOTING = 'quoting',              // 报价中
  CONFIRMING = 'confirming',        // 确认订单
  COMPLETED = 'completed',          // 完成
  SUPPORT = 'support'               // 售后支持
}

// 会话记忆：本次会话的结构化数据
interface SessionMemory {
  session_id: string;
  user_id?: string;
  started_at: number;

  // 已收集的搬家信息
  collected_data: {
    // 基本信息
    address_from?: AddressInfo;
    address_to?: AddressInfo;
    moving_date?: string;
    moving_time_preference?: string;

    // 物品信息
    items_description?: string;
    estimated_volume?: string;
    has_large_items?: boolean;
    large_items_list?: string[];

    // 服务需求
    need_packing?: boolean;
    need_dismantling?: boolean;
    special_requirements?: string;

    // 确认状态
    quote_amount?: number;
    quote_confirmed?: boolean;
    order_id?: string;
  };

  // 对话摘要（压缩后的对话历史）
  conversation_summary: string;

  // 关键时刻（重要事件不压缩）
  key_moments: Array<{
    turn_number: number;
    event_type: string;
    description: string;
    timestamp: number;
  }>;

  // 用户在本次会话表现出的特点
  session_user_traits: {
    price_sensitive?: boolean;
    time_urgent?: boolean;
    detail_oriented?: boolean;
    communication_style?: 'brief' | 'detailed';
  };
}

// 地址信息结构
interface AddressInfo {
  raw_input: string;              // 用户原始输入
  formatted_address?: string;     // 格式化地址
  city?: string;
  district?: string;
  street?: string;
  building?: string;
  floor?: number;
  has_elevator?: boolean;
  validated: boolean;             // 是否已验证
  validation_result?: any;        // 验证结果
}

// 长期记忆：用户画像
interface LongTermMemory {
  user_id: string;

  // 基本信息
  profile: {
    name?: string;
    phone?: string;
    created_at: number;
    total_orders: number;
  };

  // 常用地址
  common_addresses: Array<{
    label: string;                // 如"家"、"公司"
    address: AddressInfo;
    use_count: number;
  }>;

  // 历史订单摘要
  order_history: Array<{
    order_id: string;
    date: string;
    from_district: string;
    to_district: string;
    amount: number;
    satisfaction?: number;        // 满意度评分
    feedback?: string;
  }>;

  // 用户偏好（从历史行为中学习）
  preferences: {
    price_sensitivity: 'low' | 'medium' | 'high';
    preferred_time: string;       // 偏好的搬家时间
    communication_style: 'brief' | 'detailed';
    decision_speed: 'fast' | 'slow';
  };

  // 用户画像向量（用于个性化）
  embedding?: number[];
}
```

#### 3.2.4 记忆管理器实现

```python
class MemoryManager:
    def __init__(self, redis_client, db_client, vector_db):
        self.redis = redis_client
        self.db = db_client
        self.vector_db = vector_db
        self.llm = LLMClient()  # 用于摘要生成

    async def load_context(self, session_id: str, user_id: str = None) -> MemoryContext:
        """加载完整的记忆上下文"""

        # 并行加载三层记忆
        working, session, long_term = await asyncio.gather(
            self._load_working_memory(session_id),
            self._load_session_memory(session_id),
            self._load_long_term_memory(user_id) if user_id else None
        )

        return MemoryContext(
            working=working,
            session=session,
            long_term=long_term
        )

    async def update_after_turn(
        self,
        session_id: str,
        user_message: str,
        understanding: Understanding,
        agent_response: str
    ):
        """每轮对话后更新记忆"""

        # 1. 更新工作记忆：添加新的对话轮次
        await self._append_turn(session_id, user_message, understanding, agent_response)

        # 2. 更新会话记忆：提取并保存实体信息
        if understanding.entities:
            await self._update_collected_data(session_id, understanding.entities)

        # 3. 检查是否需要压缩
        working_memory = await self._load_working_memory(session_id)
        if len(working_memory.recent_turns) > 10:
            await self._compress_to_session_memory(session_id)

    async def _compress_to_session_memory(self, session_id: str):
        """将工作记忆压缩到会话记忆"""

        working = await self._load_working_memory(session_id)
        session = await self._load_session_memory(session_id)

        # 保留最近5轮，压缩之前的
        turns_to_compress = working.recent_turns[:-5]

        if not turns_to_compress:
            return

        # 使用LLM生成摘要
        new_summary = await self.llm.generate(f"""
请将以下对话压缩为简洁摘要，保留关键信息：

已有摘要：
{session.conversation_summary or "无"}

新对话：
{self._format_turns(turns_to_compress)}

输出更新后的完整摘要（100字以内）：
""")

        # 更新会话记忆
        session.conversation_summary = new_summary
        await self._save_session_memory(session_id, session)

        # 清理工作记忆
        working.recent_turns = working.recent_turns[-5:]
        await self._save_working_memory(session_id, working)
```

#### 3.2.5 记忆层关键设计点

| 设计点 | 说明 |
|--------|------|
| 三层分离 | 工作记忆快但小，长期记忆慢但持久 |
| 自动压缩 | 超过10轮自动压缩，避免上下文爆炸 |
| 关键时刻 | 重要事件单独记录，不会被压缩丢失 |
| 实体提取 | 每轮自动提取实体到结构化字段 |
| 渐进学习 | 长期记忆从历史会话中积累用户偏好 |

---

### 3.3 规划层（Planning Layer）

#### 3.3.1 职责

维护Agent的目标，决定每轮对话的行动策略。

**核心理念：Agent要有目标感，主动推进对话，而非纯响应式。**

#### 3.3.2 数据结构

```typescript
// 目标栈：Agent当前要完成的目标层级
interface GoalStack {
  primary_goal: Goal;              // 主目标
  current_subgoal: Goal;           // 当前子目标
  completed_subgoals: Goal[];      // 已完成的子目标
}

interface Goal {
  id: string;
  type: GoalType;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  progress?: string;               // 如 "3/5"
  blockers?: string[];             // 阻塞原因
}

enum GoalType {
  COMPLETE_ORDER = 'complete_order',       // 完成订单
  COLLECT_BASIC_INFO = 'collect_basic_info', // 收集基本信息
  COLLECT_DETAIL_INFO = 'collect_detail_info', // 收集详细信息
  GENERATE_QUOTE = 'generate_quote',       // 生成报价
  CONFIRM_ORDER = 'confirm_order',         // 确认订单
  ANSWER_QUESTION = 'answer_question',     // 回答问题
  HANDLE_EMOTION = 'handle_emotion',       // 处理情绪
  RESOLVE_ISSUE = 'resolve_issue'          // 解决问题
}

// 行动决策
interface ActionDecision {
  // 主要行动
  primary_action: Action;

  // 是否需要咨询专家
  consult_experts: ExpertType[];

  // 回应策略
  response_strategy: ResponseStrategy;

  // 下一步预期
  expected_next: string;
}

interface Action {
  type: ActionType;
  target?: string;                 // 行动目标
  parameters?: Record<string, any>;
}

enum ActionType {
  // 对话行动
  GREET = 'greet',                         // 打招呼
  ACKNOWLEDGE_EMOTION = 'acknowledge_emotion', // 回应情绪
  ANSWER_QUESTION = 'answer_question',     // 回答问题
  ASK_FOR_INFO = 'ask_for_info',           // 询问信息
  CONFIRM_INFO = 'confirm_info',           // 确认信息
  PRESENT_QUOTE = 'present_quote',         // 展示报价
  SUMMARIZE_AND_CONFIRM = 'summarize_and_confirm', // 总结确认

  // 系统行动
  CALL_TOOL = 'call_tool',                 // 调用工具
  TRANSFER_HUMAN = 'transfer_human',       // 转人工
  END_CONVERSATION = 'end_conversation'    // 结束对话
}

// 回应策略
interface ResponseStrategy {
  tone: 'warm' | 'professional' | 'empathetic' | 'enthusiastic';
  pace: 'slow' | 'normal' | 'quick';       // 对话节奏
  focus: string;                           // 本轮重点
  avoid: string[];                         // 避免的内容
  max_questions: number;                   // 最多问几个问题
}
```

#### 3.3.3 规划器实现

```python
class PlanningLayer:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def decide_action(
        self,
        understanding: Understanding,
        memory: MemoryContext,
        current_goals: GoalStack
    ) -> ActionDecision:
        """决定下一步行动"""

        # 1. 优先级判断：情绪 > 问题 > 目标推进
        if understanding.emotion.needs_attention:
            return self._plan_emotional_response(understanding, memory)

        if understanding.meta.is_question:
            return self._plan_answer_question(understanding, memory, current_goals)

        if understanding.meta.requires_human:
            return ActionDecision(
                primary_action=Action(type=ActionType.TRANSFER_HUMAN),
                consult_experts=[],
                response_strategy=self._get_strategy('empathetic')
            )

        # 2. 正常目标推进
        return await self._plan_goal_advancement(understanding, memory, current_goals)

    def _plan_emotional_response(
        self,
        understanding: Understanding,
        memory: MemoryContext
    ) -> ActionDecision:
        """规划情绪回应"""

        return ActionDecision(
            primary_action=Action(
                type=ActionType.ACKNOWLEDGE_EMOTION,
                parameters={
                    "emotion": understanding.emotion,
                    "then": "gently_return_to_topic"
                }
            ),
            consult_experts=[ExpertType.EMOTIONAL],
            response_strategy=ResponseStrategy(
                tone='empathetic',
                pace='slow',
                focus='用户的感受',
                avoid=['立刻转业务', '说"别担心"', '讲道理'],
                max_questions=0
            ),
            expected_next="用户情绪缓和后继续"
        )
```

#### 3.3.4 规划层关键设计点

| 设计点 | 说明 |
|--------|------|
| 优先级明确 | 情绪 > 问题 > 目标，不会在用户焦虑时追问地址 |
| 目标栈 | 主目标分解为子目标，有清晰的进度感 |
| 策略分离 | 行动（做什么）和策略（怎么做）分开 |
| 上下文感知 | 根据已收集信息动态调整下一步 |
| 自然过渡 | acknowledge_first确保先确认再追问 |

---

## 第四部分：专家顾问系统设计

### 4.1 系统概述

**核心理念：专家提供建议，不接管对话。**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          专家顾问系统                                    │
│                                                                          │
│   主Agent提问 ──▶ 专家分析 ──▶ 返回建议 ──▶ 主Agent决定是否采纳          │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │  情感顾问  │  │  知识顾问  │  │  业务顾问  │  │  订单顾问  │         │
│  │            │  │            │  │            │  │            │         │
│  │  实现方式  │  │  实现方式  │  │  实现方式  │  │  实现方式  │         │
│  │  LLM       │  │  RAG+LLM   │  │  规则+LLM  │  │  规则      │         │
│  │            │  │            │  │            │  │            │         │
│  │  输出      │  │  输出      │  │  输出      │  │  输出      │         │
│  │  回应建议  │  │  知识答案  │  │  计算结果  │  │  状态校验  │         │
│  │  语气指导  │  │  参考来源  │  │  规则提醒  │  │  下一步骤  │         │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 情感顾问（Emotional Advisor）

#### 4.2.1 职责

分析用户情绪，提供情感回应建议和对话策略。

#### 4.2.2 数据结构

```typescript
// 情感顾问的建议
interface EmotionalAdvice {
  // 情绪解读
  emotion_interpretation: {
    primary_emotion: string;
    underlying_needs: string[];
    triggers: string[];
  };

  // 回应建议
  response_suggestions: {
    acknowledgment: string;
    tone: string;
    pacing: string;
    do_list: string[];
    avoid_list: string[];
  };

  // 过渡策略
  transition_strategy: {
    when_to_transition: string;
    how_to_transition: string;
    bridge_sentence?: string;
  };

  // 风险提示
  risk_assessment: {
    escalation_risk: 'low' | 'medium' | 'high';
    needs_human: boolean;
    reason?: string;
  };
}
```

### 4.3 知识顾问（Knowledge Advisor）

#### 4.3.1 职责

基于RAG检索搬家知识库，回答用户的专业问题。

#### 4.3.2 知识库结构

```typescript
interface KnowledgeItem {
  id: string;
  category: KnowledgeCategory;
  question: string;
  answer: string;
  keywords: string[];
  related_items: string[];
  source: string;
  last_updated: number;
  embedding?: number[];
}

enum KnowledgeCategory {
  PRICING = 'pricing',
  PROCESS = 'process',
  PACKING = 'packing',
  FURNITURE = 'furniture',
  SPECIAL_ITEMS = 'special_items',
  INSURANCE = 'insurance',
  TIMING = 'timing',
  TIPS = 'tips',
  FAQ = 'faq'
}
```

### 4.4 业务顾问（Business Advisor）

#### 4.4.1 职责

提供业务规则校验、报价计算、地址验证等业务支持。

#### 4.4.2 报价规则配置

```typescript
interface PricingRules {
  base_prices: {
    same_district: number;
    cross_district: number;
    cross_city: number;
  };

  floor_charges: {
    no_elevator_per_floor: number;
    elevator_available: number;
  };

  large_items: {
    [itemType: string]: number;
  };

  time_adjustments: {
    weekend_multiplier: number;
    holiday_multiplier: number;
    peak_month_extra: number;
  };

  services: {
    packing_per_hour: number;
    dismantling_per_item: number;
    storage_per_day: number;
  };
}
```

### 4.5 订单顾问（Order Advisor）

#### 4.5.1 职责

管理订单状态，校验必填字段，控制流程进度。

#### 4.5.2 订单状态

```typescript
enum OrderStatus {
  DRAFT = 'draft',
  INFO_COMPLETE = 'info_complete',
  QUOTED = 'quoted',
  CONFIRMED = 'confirmed',
  PAID = 'paid',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}
```

### 4.6 专家顾问系统关键设计点

| 设计点 | 说明 |
|--------|------|
| **建议而非指令** | 所有专家返回的是建议，主Agent决定是否采纳 |
| **混合实现** | 情感用LLM、知识用RAG+LLM、业务用规则+LLM、订单用纯规则 |
| **并行咨询** | 可同时咨询多个专家，减少延迟 |
| **置信度** | 知识顾问返回置信度，低置信度时主Agent可选择不采纳 |
| **知识积累** | 知识顾问支持从对话中学习，逐步丰富知识库 |
| **规则透明** | 业务规则配置化，便于调整 |

---

## 第五部分：生成层与工具箱设计

### 5.1 生成层（Response Generator）

#### 5.1.1 职责

综合理解层、记忆层、规划层、专家顾问的信息，生成最终的自然语言回复。

**核心理念：这是唯一对外输出的地方，保证人格统一、语言自然。**

#### 5.1.2 人格配置

```python
DEFAULT_PERSONA = PersonaConfig(
    name="小搬",
    traits=["耐心", "专业", "温暖", "细心"],
    tone_guidelines={
        "default": "友好专业，像一个靠谱的朋友在帮忙",
        "empathetic": "温和关切，先理解感受，不急于推进业务",
        "professional": "专业可靠，给出明确的信息和建议",
        "warm": "亲切自然，让用户感到被关心",
        "enthusiastic": "积极热情，对用户的计划表示支持"
    },
    avoid_patterns=[
        "别担心",
        "非常抱歉",
        "亲",
        "您好，我是智能助手",
        "请问您",
        "好的呢",
        "哦哦",
        "嗯嗯嗯"
    ]
)
```

### 5.2 工具箱（Tool Box）

工具箱提供Agent调用外部能力的接口：

- **地图服务工具**：地址解析、验证、距离计算
- **图片识别工具**：识别家具物品，估算搬家体积
- **订单系统工具**：创建、查询、更新订单
- **可用性检查工具**：查询日期、时段的可用性

---

## 第六部分：整体流程与技术选型

### 6.1 技术栈

```
前端层：React / Vue 3 + Ant Design Mobile
后端层：Python 3.11+ + FastAPI + asyncio
AI/ML层：GPT-4o / 通义千问-Max + text-embedding-3-small
数据层：Redis + PostgreSQL + Qdrant
外部服务：高德地图 API + 微信支付
```

### 6.2 部署架构

```
CDN/WAF → Nginx负载均衡 → Agent服务集群 → 数据层
```

### 6.3 性能优化策略

- 并行执行专家咨询
- 简化路径跳过不必要的步骤
- 流式输出降低感知延迟
- 常见问答缓存

### 6.4 实现阶段规划

| 阶段 | 内容 | 周期 |
|------|------|------|
| 阶段一 MVP | 基础对话、信息收集、报价、订单 | 3个月 |
| 阶段二 | 情感处理、图片识别、快捷回复 | 2个月 |
| 阶段三 | RAG知识库、长期记忆、个性化 | 2个月 |
| 阶段四 | 性能优化、监控完善、规模化 | 持续 |

---

## 第七部分：数据库设计与API接口定义

### 7.1 核心表设计

- **users**：用户表
- **sessions**：会话表
- **messages**：消息表
- **orders**：订单表
- **user_profiles**：用户画像表
- **knowledge_items**：知识条目表
- **feedback**：反馈表

### 7.2 核心API

- `POST /api/v1/chat/message`：发送消息
- `POST /api/v1/chat/message/stream`：流式发送消息
- `GET /api/v1/chat/sessions/{id}`：获取会话详情
- `GET /api/v1/orders`：获取订单列表
- `POST /api/v1/orders/{id}/confirm`：确认订单
- `POST /api/v1/tools/upload-image`：上传图片
- `POST /api/v1/tools/validate-address`：验证地址

---

## 第八部分：对话示例与测试用例

### 8.1 典型对话流程

#### 完整下单流程

```
用户: 你好，我想搬家
助手: 你好呀！搬家的事找我就对了。请问您是从哪里搬到哪里呢？

用户: 从朝阳区望京搬到海淀区中关村
助手: 好的，从望京搬到中关村，记下了。请问您计划什么时候搬呢？
    [快捷回复: 这周末 | 下周 | 月底 | 还没定]

用户: 这周六吧，1月20号
助手: 1月20号周六，了解。请问大概有多少东西要搬呢？

用户: 一室一厅，有张双人床、一个三人沙发、书桌
助手: 明白，一室一厅，有床、沙发、书桌这些大件。望京那边是几楼？有电梯吗？

用户: 两边都15楼有电梯
助手: 好的，两边都有电梯，搬运会方便很多。

    📦 搬家报价单
    跨区搬家基础费：¥400
    总计：¥400

    这个价格您看可以吗？
    [快捷回复: 确认预约 | 我再考虑一下 | 能便宜点吗]

用户: 可以，确认预约
助手: 太好了！已为您预约1月20号周六的搬家服务。

    📋 订单号：MV20240115001
    搬家当天师傅会提前联系您确认具体时间。有任何问题随时找我！
```

### 8.2 测试覆盖要求

| 测试类型 | 覆盖要求 |
|---------|---------|
| 单元测试 | > 80% |
| 集成测试 | 核心流程 100% |
| 性能测试 | P99 < 3s |
| 回归测试 | 每次发布 |

---

## 第九部分：风险与应对 + 总结

### 9.1 主要风险

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| LLM服务不稳定 | 高 | 多模型备份 + 降级方案 |
| 响应延迟过高 | 高 | 流式输出 + 并行处理 + 缓存 |
| 情感识别失误 | 中 | 保守策略 + 兜底检测 + 快速转人工 |
| 知识库不足 | 中 | 初期人工编写FAQ + 从对话学习 |
| 报价不准确 | 中 | 报价说明预估性质 + 定期校准 |

### 9.2 监控指标

- 请求成功率 > 99%
- P99延迟 < 3秒
- 转化率 > 15%
- 转人工率 < 10%
- 用户满意度 > 4.0/5

### 9.3 项目总结

**核心设计要点：**

1. **主Agent + 专家顾问架构** - 解决人格不一致问题
2. **四层处理流程** - 理解→记忆→规划→生成
3. **情绪优先原则** - 先处理情绪，再处理业务
4. **对话式信息收集** - 每次只问1-2个问题
5. **渐进式能力构建** - MVP先跑通，逐步完善

---

## 第十部分：设计深度分析报告

### 10.1 整体评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 架构设计 | ⭐⭐⭐⭐☆ | 整体架构清晰，但部分细节待完善 |
| 组件设计 | ⭐⭐⭐⭐⭐ | 各组件职责明确，接口定义清晰 |
| 技术选型 | ⭐⭐⭐⭐☆ | 选型合理，但缺乏详细对比论证 |
| 可落地性 | ⭐⭐⭐☆☆ | 设计偏理想化，实际落地有挑战 |

### 10.2 需要重点关注的问题

1. **单Agent承载过重** - 考虑拆分为"理解Agent"和"对话Agent"
2. **专家顾问调用规则不清** - 需要制定明确的决策树
3. **简化/完整路径边界模糊** - 需要更严格的判断条件
4. **成本估算缺失** - 需要精确估算LLM成本
5. **MVP范围过大** - 建议先做MVP-0验证核心流程

### 10.3 改进建议

**架构层面：**
- 考虑拆分主Agent降低复杂度
- 制定明确的专家调用决策树
- 简化情感处理，合并到理解层

**实现层面：**
- 并行处理、流式输出、缓存优化
- 使用国产模型控制成本
- 建立Prompt测试集和版本管理

**工程层面：**
- 先做MVP-0验证核心流程（2-4周）
- 制定明确的里程碑和验收标准
- 补充Prompt测试、对话质量评估

### 10.4 建议的MVP-0范围（2-4周）

只做最核心的事情：
1. 一个能对话的基础Agent（简单理解+简单记忆+简单回复）
2. 能收集核心信息（出发地、目的地、日期）
3. 能给出报价（固定规则计算）

**不做的事情：**
- 复杂的理解层解析
- 三层记忆系统
- 规划层目标栈
- 专家顾问系统
- 情绪处理
- 图片识别
- RAG知识库

---

## 附录

### A. 参考资料

- 蚂蚁阿福产品分析
- LangGraph文档
- RAG最佳实践

### B. 术语表

| 术语 | 说明 |
|------|------|
| Agent | 智能对话代理 |
| RAG | 检索增强生成 |
| Embedding | 向量嵌入 |
| Prompt | 提示词 |

### C. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| V1.0 | 2026-01-29 | 初版设计文档 |

---

*文档结束*
