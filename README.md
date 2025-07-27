# 提示词追踪系统

透明化的LLM提示词变化管理系统，记录每次提示词的动态变化过程。

## 🎯 系统用途

这个系统专门用于追踪LLM提示词的动态构建过程：

1. **初始化提示词**: 记录Agent的初始提示词模板
2. **用户输入追加**: 记录`<UserInput>内容</UserInput>`的添加
3. **系统标记追加**: 记录`<Start><SessionId>xxx</SessionId><Reason>xxx</Reason></Start>`的添加
4. **LLM输出追加**: 记录LLM生成的`<Thought>`、`<Action>`、`<ActionInput>`等内容的添加

每次变化都会在数据库中记录**完整的提示词内容**，让您能够完全透明地看到提示词是如何一步步构建的。

## ✨ 核心特性

- **提示词变化追踪**: 记录每次提示词的增量变化
- **完整历史记录**: 保存每个变化后的完整提示词内容
- **自动信息提取**: 从LLM输出中提取工具调用和用户交互信息
- **会话管理**: 支持多个并发会话的独立管理
- **RESTful API**: 提供完整的API接口
- **数据持久化**: 使用MySQL数据库存储

## 🏗️ 系统架构

```
prompt-tracker/
├── database/           # 数据库连接和表结构
│   ├── connection.py   # 数据库连接管理
│   ├── schema.sql      # 数据库表结构
│   └── __init__.py
├── models/             # 数据模型定义
│   ├── prompt_models.py # 提示词追踪相关模型
│   └── __init__.py
├── core/               # 核心业务逻辑
│   ├── prompt_tracker.py # 提示词追踪器
│   └── __init__.py
├── api/                # REST API接口
│   ├── prompt_routes.py # API路由定义
│   └── __init__.py
├── config/             # 配置管理
│   ├── settings.py     # 配置文件
│   └── __init__.py
├── main.py             # 主应用入口
├── demo.py             # 系统功能演示
├── test_db_connection.py # 数据库连接测试
└── README.md           # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用uv安装依赖（推荐）
uv sync

# 或使用pip
pip install -e .
```

### 2. 配置数据库

系统默认连接到您提供的MySQL数据库：
- 主机: ****
- 用户: ****
- 密码: ****
- 数据库: ****

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 4. 运行演示

```bash
# 测试数据库连接
python test_db_connection.py

# 运行系统功能演示
python demo.py
```

### 5. 查看API文档

访问 `http://localhost:8000/docs` 查看完整的API文档

## 📊 使用示例

### 创建会话并追踪提示词变化

```python
import requests

base_url = "http://localhost:8000/api/v1"

# 1. 创建会话
response = requests.post(f"{base_url}/sessions", json={
    "session_id": "my_session_001"
})
print("会话创建:", response.json())

# 2. 添加用户输入
response = requests.post(f"{base_url}/sessions/my_session_001/user-input", json={
    "session_id": "my_session_001",
    "user_input": "帮我写一个Python函数"
})
print("用户输入:", response.json())

# 3. 添加系统标记
response = requests.post(f"{base_url}/sessions/my_session_001/system-marker", json={
    "session_id": "my_session_001",
    "reason": "UserInput"
})
print("系统标记:", response.json())

# 4. 添加LLM输出
llm_output = """<Thought>用户需要一个Python函数，我需要了解具体需求</Thought>
<UserInteraction>请告诉我您需要什么功能的Python函数？</UserInteraction>
<End><Reason>UserInteraction</Reason></End>"""

response = requests.post(f"{base_url}/sessions/my_session_001/llm-output", json={
    "session_id": "my_session_001",
    "llm_output": llm_output
})
print("LLM输出:", response.json())

# 5. 查看当前完整提示词
response = requests.get(f"{base_url}/sessions/my_session_001/current-prompt")
print("当前提示词长度:", response.json()["prompt_length"])

# 6. 查看变化历史
response = requests.get(f"{base_url}/sessions/my_session_001/changes")
print("变化历史:", len(response.json()), "次变化")
```

## 🔧 API接口

### 会话管理
- `POST /api/v1/sessions` - 创建新会话
- `GET /api/v1/sessions` - 获取会话列表
- `GET /api/v1/sessions/{session_id}` - 获取会话详情

### 提示词追踪
- `POST /api/v1/sessions/{session_id}/user-input` - 添加用户输入
- `POST /api/v1/sessions/{session_id}/system-marker` - 添加系统标记
- `POST /api/v1/sessions/{session_id}/llm-output` - 添加LLM输出
- `GET /api/v1/sessions/{session_id}/current-prompt` - 获取当前完整提示词

### 数据查询
- `GET /api/v1/sessions/{session_id}/changes` - 获取提示词变化历史
- `GET /api/v1/sessions/{session_id}/tool-calls` - 获取工具调用记录
- `GET /api/v1/sessions/{session_id}/interactions` - 获取用户交互记录
- `GET /api/v1/stats` - 获取系统统计信息

## 📈 数据库设计

### 主要数据表
- **sessions**: 会话信息表，存储会话ID和初始提示词
- **prompt_changes**: 提示词变化记录表，存储每次变化的完整提示词
- **tool_calls**: 工具调用记录表，从LLM输出中提取的工具调用信息
- **user_interactions**: 用户交互记录表，从LLM输出中提取的交互信息

### 变化类型
- `init`: 初始化提示词
- `user_input`: 用户输入
- `system_marker`: 系统标记（Start/End）
- `llm_output`: LLM输出

## 🎯 系统价值

1. **透明化**: 完全透明地看到提示词的构建过程
2. **可追溯**: 每次变化都有完整记录，支持回溯分析
3. **数据驱动**: 为LLM优化提供详实的数据支持
4. **易于集成**: 提供完整的REST API，易于与现有系统集成

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个系统！
