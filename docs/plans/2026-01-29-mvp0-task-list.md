# MVP-0 最小验证版本任务列表

> 目标：2周内完成，验证核心对话流程可行性
> 日期：2026-01-29
> 更新：根据团队情况调整（DeepSeek + SQLite + 前端 + Vibe Coding）

---

## MVP-0 目标

**做什么：**
- 一个能自然对话的基础Agent
- 能收集核心搬家信息（出发地、目的地、日期）
- 能给出报价
- 简单的H5对话界面

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

## 技术选型（MVP-0简化版）

| 组件 | 选择 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | 异步支持好，开发快 |
| LLM | **DeepSeek** | 成本极低，中文能力强 |
| 数据库 | **SQLite** | 零配置，开发简单，后期可换PostgreSQL |
| 会话存储 | **SQLite** | 简化架构，不用Redis |
| 前端 | **Vue 3 + Vant** | 移动端H5，组件丰富 |
| 部署 | **本地Docker** | 先跑通，后期再上云 |

---

## 任务分解

### 阶段一：项目初始化（1天）

#### 1.1 后端项目结构
- [ ] 创建Python项目结构
  ```
  src/
  ├── agent/           # Agent核心
  │   ├── __init__.py
  │   ├── core.py      # 主Agent
  │   ├── prompts.py   # Prompt模板
  │   └── memory.py    # 简单记忆
  ├── services/        # 业务服务
  │   ├── __init__.py
  │   ├── quote.py     # 报价计算
  │   └── order.py     # 订单服务
  ├── api/             # API接口
  │   ├── __init__.py
  │   ├── main.py      # FastAPI入口
  │   └── routes.py    # 路由定义
  ├── models/          # 数据模型
  │   ├── __init__.py
  │   ├── schemas.py   # Pydantic模型
  │   └── database.py  # SQLite模型
  └── config.py        # 配置
  ```
- [ ] 配置requirements.txt
  ```
  fastapi==0.109.0
  uvicorn[standard]==0.27.0
  openai==1.12.0  # DeepSeek兼容OpenAI接口
  sqlalchemy==2.0.25
  pydantic==2.6.0
  python-dotenv==1.0.0
  ```
- [ ] 配置.env（DeepSeek API Key）

#### 1.2 前端项目结构
- [ ] 创建Vue 3项目
  ```
  web/
  ├── src/
  │   ├── views/
  │   │   └── Chat.vue      # 对话页面
  │   ├── components/
  │   │   ├── MessageList.vue   # 消息列表
  │   │   ├── MessageInput.vue  # 输入框
  │   │   └── QuoteCard.vue     # 报价卡片
  │   ├── api/
  │   │   └── chat.js       # API调用
  │   ├── App.vue
  │   └── main.js
  ├── package.json
  └── vite.config.js
  ```
- [ ] 安装依赖（Vue 3 + Vant + Axios）

---

### 阶段二：核心Agent实现（3-4天）

#### 2.1 DeepSeek客户端配置
- [ ] 配置DeepSeek API（兼容OpenAI接口）
  ```python
  from openai import OpenAI

  client = OpenAI(
      api_key="your-deepseek-api-key",
      base_url="https://api.deepseek.com/v1"
  )
  ```
- [ ] 封装LLM调用方法
- [ ] 实现流式响应

#### 2.2 简单记忆系统（SQLite）
- [ ] 设计会话表
  ```sql
  CREATE TABLE sessions (
      id TEXT PRIMARY KEY,
      messages TEXT,        -- JSON存储对话历史
      collected_data TEXT,  -- JSON存储已收集信息
      stage TEXT,           -- 当前阶段
      created_at TIMESTAMP,
      updated_at TIMESTAMP
  );
  ```
- [ ] 设计订单表
  ```sql
  CREATE TABLE orders (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      address_from TEXT,
      address_to TEXT,
      moving_date TEXT,
      floor_from INTEGER,
      floor_to INTEGER,
      has_elevator_from BOOLEAN,
      has_elevator_to BOOLEAN,
      items_description TEXT,
      quote_amount REAL,
      status TEXT,
      created_at TIMESTAMP
  );
  ```
- [ ] 实现SQLAlchemy模型
- [ ] 实现会话CRUD

#### 2.3 Prompt设计
- [ ] 系统Prompt
  ```
  你是"小搬"，一个耐心、专业、温暖的搬家助手。

  【你的任务】
  帮助用户完成搬家预约，需要收集以下信息：
  - 搬出地址（必填）
  - 搬入地址（必填）
  - 搬家日期（必填）
  - 楼层和电梯情况（可选）
  - 物品描述（可选）

  【对话风格】
  - 像朋友聊天一样自然，不要像机器人
  - 每次只问1-2个问题，不要一次问太多
  - 用户提供信息后，先确认再问下一个
  - 不要说"别担心"、"亲"这类词

  【输出格式】
  每次回复需要输出JSON格式：
  {
    "reply": "你要说的话",
    "extracted_info": {
      "address_from": "提取到的搬出地址或null",
      "address_to": "提取到的搬入地址或null",
      "moving_date": "提取到的日期或null",
      "floor_from": "楼层数字或null",
      "floor_to": "楼层数字或null",
      "has_elevator_from": "true/false/null",
      "has_elevator_to": "true/false/null",
      "items_description": "物品描述或null"
    },
    "stage": "collecting/quoting/confirming/completed"
  }
  ```
- [ ] 报价展示Prompt
- [ ] 订单确认Prompt

#### 2.4 主Agent实现
- [ ] 实现Agent类
  ```python
  class MovingAgent:
      async def chat(self, session_id: str, message: str) -> AgentResponse:
          # 1. 加载/创建会话
          session = await self.get_or_create_session(session_id)

          # 2. 构建消息列表
          messages = self.build_messages(session, message)

          # 3. 调用DeepSeek
          response = await self.call_llm(messages)

          # 4. 解析JSON响应
          parsed = self.parse_response(response)

          # 5. 更新会话状态
          await self.update_session(session, message, parsed)

          # 6. 如果信息完整，计算报价
          if self.is_info_complete(session):
              quote = self.calculate_quote(session)
              parsed['quote'] = quote

          return parsed
  ```
- [ ] 实现信息完整性检查
- [ ] 实现阶段流转逻辑

---

### 阶段三：业务服务实现（1-2天）

#### 3.1 报价计算
- [ ] 定义报价规则
  ```python
  PRICING = {
      "base_price": 300,           # 基础价格
      "cross_district_extra": 100, # 跨区加价
      "floor_no_elevator": 50,     # 无电梯每层
      "weekend_multiplier": 1.1,   # 周末加价
  }
  ```
- [ ] 实现报价计算函数
- [ ] 生成报价明细

#### 3.2 订单服务
- [ ] 实现创建订单
- [ ] 实现查询订单
- [ ] 实现确认订单

---

### 阶段四：API接口实现（1天）

#### 4.1 对话接口
- [ ] POST /api/chat - 发送消息
  ```python
  @router.post("/chat")
  async def chat(request: ChatRequest):
      response = await agent.chat(
          session_id=request.session_id or str(uuid4()),
          message=request.message
      )
      return response
  ```
- [ ] GET /api/sessions/{id} - 获取会话

#### 4.2 订单接口
- [ ] GET /api/orders/{id} - 获取订单
- [ ] POST /api/orders/{id}/confirm - 确认订单

#### 4.3 配置CORS
- [ ] 允许前端跨域访问

---

### 阶段五：前端开发（2-3天）

#### 5.1 对话界面
- [ ] 消息列表组件
  - 用户消息（右侧，蓝色气泡）
  - Agent消息（左侧，灰色气泡）
  - 支持Markdown渲染
- [ ] 输入框组件
  - 文本输入
  - 发送按钮
  - 加载状态
- [ ] 快捷回复组件
  - 显示建议回复按钮
  - 点击自动发送

#### 5.2 报价卡片
- [ ] 报价展示卡片
  - 价格明细
  - 确认按钮
- [ ] 订单确认卡片
  - 订单信息汇总
  - 确认/取消按钮

#### 5.3 API对接
- [ ] 封装API调用
- [ ] 处理加载状态
- [ ] 处理错误提示

#### 5.4 样式优化
- [ ] 移动端适配
- [ ] 对话气泡样式
- [ ] 整体视觉优化

---

### 阶段六：联调与测试（1-2天）

#### 6.1 前后端联调
- [ ] 对话流程联调
- [ ] 报价展示联调
- [ ] 订单确认联调

#### 6.2 对话测试
- [ ] 正常流程测试
- [ ] 信息分多次提供
- [ ] 信息修改测试
- [ ] 边界情况测试

#### 6.3 Prompt调优
- [ ] 收集不理想的回复
- [ ] 优化Prompt

---

### 阶段七：Docker部署（0.5天）

#### 7.1 后端Docker
- [ ] 编写Dockerfile
- [ ] 编写docker-compose.yml

#### 7.2 前端构建
- [ ] 构建静态文件
- [ ] Nginx配置

---

## 时间规划（Vibe Coding加速版）

| 阶段 | 任务 | 预估时间 |
|------|------|---------|
| 阶段一 | 项目初始化 | 0.5-1天 |
| 阶段二 | 核心Agent实现 | 2-3天 |
| 阶段三 | 业务服务实现 | 1天 |
| 阶段四 | API接口实现 | 0.5-1天 |
| 阶段五 | 前端开发 | 2-3天 |
| 阶段六 | 联调与测试 | 1-2天 |
| 阶段七 | Docker部署 | 0.5天 |
| **总计** | | **8-11天（约2周）** |

---

## 验收标准

### 功能验收
- [ ] 能完成基本对话，收集搬家信息
- [ ] 能根据信息生成报价
- [ ] 能创建订单
- [ ] 对话自然，不像填表单
- [ ] H5界面可用，体验流畅

### 性能验收
- [ ] 单次响应延迟 < 3秒
- [ ] 前端加载 < 2秒

---

## 风险与应对

| 风险 | 应对 |
|------|------|
| DeepSeek响应不稳定 | 设置超时+重试，准备兜底话术 |
| JSON解析失败 | 设计容错机制，多次尝试 |
| Prompt效果不好 | 预留调优时间，收集bad case迭代 |

---

## DeepSeek API 信息

**API文档：** https://platform.deepseek.com/api-docs

**调用示例：**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个搬家助手"},
        {"role": "user", "content": "我想搬家"}
    ],
    stream=True  # 支持流式
)
```

**价格：** 约 ¥1/百万tokens（极低）

---

*文档结束*
