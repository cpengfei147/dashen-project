# MVP-0 最小验证版本任务列表

> 目标：2-4周内完成，验证核心对话流程可行性
> 日期：2026-01-29

---

## MVP-0 目标

**做什么：**
- 一个能自然对话的基础Agent
- 能收集核心搬家信息（出发地、目的地、日期）
- 能给出报价

**不做什么：**
- ❌ 复杂的多维度理解层
- ❌ 三层记忆系统（只用简单的会话记忆）
- ❌ 规划层目标栈
- ❌ 专家顾问系统
- ❌ 情绪处理
- ❌ 图片识别
- ❌ RAG知识库
- ❌ 长期用户画像

---

## 任务分解

### 阶段一：项目初始化（2-3天）

#### 1.1 项目结构搭建
- [ ] 创建Python项目结构
  ```
  dashen-project/
  ├── src/
  │   ├── agent/           # Agent核心
  │   │   ├── __init__.py
  │   │   ├── core.py      # 主Agent
  │   │   ├── prompts.py   # Prompt模板
  │   │   └── memory.py    # 简单记忆
  │   ├── services/        # 业务服务
  │   │   ├── __init__.py
  │   │   ├── quote.py     # 报价计算
  │   │   └── order.py     # 订单服务
  │   ├── api/             # API接口
  │   │   ├── __init__.py
  │   │   ├── main.py      # FastAPI入口
  │   │   └── routes.py    # 路由定义
  │   ├── models/          # 数据模型
  │   │   ├── __init__.py
  │   │   └── schemas.py   # Pydantic模型
  │   └── config.py        # 配置
  ├── tests/               # 测试
  ├── requirements.txt
  ├── .env.example
  └── README.md
  ```
- [ ] 配置依赖管理（requirements.txt）
- [ ] 配置环境变量（.env）
- [ ] 配置日志

#### 1.2 基础设施
- [ ] 配置LLM客户端（OpenAI/通义千问）
- [ ] 配置Redis连接（会话存储）
- [ ] 配置PostgreSQL连接（订单存储）
- [ ] 编写配置加载模块

---

### 阶段二：核心Agent实现（5-7天）

#### 2.1 简单记忆系统
- [ ] 设计会话数据结构
  ```python
  class SessionData:
      session_id: str
      messages: List[Message]  # 最近N轮对话
      collected_data: dict     # 已收集的信息
      stage: str               # 当前阶段
      created_at: datetime
  ```
- [ ] 实现Redis存储/读取
- [ ] 实现会话过期清理

#### 2.2 Prompt设计
- [ ] 设计系统Prompt（人格设定）
  ```
  你是"小搬"，一个耐心、专业、温暖的搬家助手。
  你的目标是帮助用户完成搬家预约。

  对话风格：
  - 像朋友聊天一样自然
  - 每次只问1-2个问题
  - 先确认收到的信息，再追问下一个
  ...
  ```
- [ ] 设计信息收集Prompt
- [ ] 设计报价展示Prompt
- [ ] 设计确认订单Prompt

#### 2.3 主Agent实现
- [ ] 实现Agent核心类
  ```python
  class MovingAgent:
      async def chat(self, session_id: str, message: str) -> AgentResponse:
          # 1. 加载会话
          # 2. 构建Prompt（系统+历史+用户消息）
          # 3. 调用LLM
          # 4. 解析响应，提取实体
          # 5. 更新会话状态
          # 6. 返回响应
  ```
- [ ] 实现实体提取（从LLM响应中提取结构化数据）
- [ ] 实现阶段判断（收集中/报价中/确认中）
- [ ] 实现流式响应支持

#### 2.4 对话流程控制
- [ ] 实现信息收集流程
  - 必填：address_from, address_to, moving_date
  - 可选：floor_from, floor_to, has_elevator, items_description
- [ ] 实现信息确认流程
- [ ] 实现报价触发条件（必填信息收集完成）
- [ ] 实现订单确认流程

---

### 阶段三：业务服务实现（3-4天）

#### 3.1 报价计算服务
- [ ] 设计报价规则配置
  ```python
  PRICING_CONFIG = {
      "base_prices": {
          "same_district": 300,
          "cross_district": 400,
          "cross_city": 800
      },
      "floor_charges": {
          "no_elevator_per_floor": 50
      },
      "time_adjustments": {
          "weekend_multiplier": 1.1
      }
  }
  ```
- [ ] 实现报价计算逻辑
- [ ] 实现报价明细生成

#### 3.2 订单服务
- [ ] 设计订单表结构
- [ ] 实现订单创建
- [ ] 实现订单查询
- [ ] 实现订单状态更新

#### 3.3 地址处理（简化版）
- [ ] 实现简单的地址解析（提取区/街道）
- [ ] 实现同区/跨区判断
- [ ] （可选）集成地图API验证地址

---

### 阶段四：API接口实现（2-3天）

#### 4.1 核心接口
- [ ] POST /api/v1/chat/message - 发送消息
  ```python
  @router.post("/message")
  async def send_message(request: SendMessageRequest):
      # session_id, message
      # 返回: reply, collected_data, stage
  ```
- [ ] POST /api/v1/chat/message/stream - 流式发送消息
- [ ] GET /api/v1/chat/sessions/{id} - 获取会话详情

#### 4.2 订单接口
- [ ] GET /api/v1/orders - 获取订单列表
- [ ] GET /api/v1/orders/{id} - 获取订单详情
- [ ] POST /api/v1/orders/{id}/confirm - 确认订单

#### 4.3 基础设施
- [ ] 实现错误处理中间件
- [ ] 实现请求日志
- [ ] 实现CORS配置

---

### 阶段五：测试与调试（3-4天）

#### 5.1 单元测试
- [ ] Agent核心逻辑测试
- [ ] 报价计算测试
- [ ] 订单服务测试

#### 5.2 对话测试
- [ ] 正常流程测试（完整下单）
- [ ] 信息补充测试（分多次提供信息）
- [ ] 信息修改测试（纠正之前的信息）
- [ ] 边界情况测试（空消息、超长消息等）

#### 5.3 Prompt调优
- [ ] 收集测试对话样本
- [ ] 分析不理想的回复
- [ ] 迭代优化Prompt

#### 5.4 性能测试
- [ ] 测试单次响应延迟
- [ ] 测试并发处理能力

---

### 阶段六：部署与文档（1-2天）

#### 6.1 部署
- [ ] 编写Dockerfile
- [ ] 编写docker-compose.yml
- [ ] 部署到测试环境

#### 6.2 文档
- [ ] 编写API文档
- [ ] 编写部署说明
- [ ] 编写测试说明

---

## 验收标准

### 功能验收
- [ ] 能完成基本对话，收集搬家信息
- [ ] 能根据信息生成报价
- [ ] 能创建订单
- [ ] 对话自然，不像填表单

### 性能验收
- [ ] 单次响应延迟 < 3秒
- [ ] 支持 10 QPS 并发

### 质量验收
- [ ] 核心流程测试通过
- [ ] 无阻塞性Bug

---

## 时间规划

| 阶段 | 任务 | 预估时间 |
|------|------|---------|
| 阶段一 | 项目初始化 | 2-3天 |
| 阶段二 | 核心Agent实现 | 5-7天 |
| 阶段三 | 业务服务实现 | 3-4天 |
| 阶段四 | API接口实现 | 2-3天 |
| 阶段五 | 测试与调试 | 3-4天 |
| 阶段六 | 部署与文档 | 1-2天 |
| **总计** | | **16-23天（约3-4周）** |

---

## 技术选型（MVP-0简化版）

| 组件 | 选择 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | 异步支持好，开发快 |
| LLM | 通义千问-Max 或 GPT-4o-mini | 成本考虑，先用便宜的 |
| 会话存储 | Redis | 简单快速 |
| 订单存储 | PostgreSQL | 可靠持久 |
| 部署 | Docker | 便于部署和迁移 |

---

## 风险与应对

| 风险 | 应对 |
|------|------|
| LLM响应不稳定 | 设置超时+重试，准备兜底话术 |
| 实体提取不准确 | 用JSON格式输出，降低解析难度 |
| Prompt效果不好 | 预留调优时间，收集bad case迭代 |
| 时间不够 | 优先保证核心流程，其他功能可砍 |

---

## 下一步（MVP-0完成后）

MVP-0验证成功后，进入MVP-1：
- 添加情绪识别和处理
- 添加图片识别
- 完善记忆系统
- 添加知识问答（RAG）

---

*文档结束*
