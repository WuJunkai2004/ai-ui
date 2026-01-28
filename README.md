# GenUI Agent Backend

本项目是基于 AI Agent 的后端系统，旨在连接模糊的用户意图与精确的执行操作。

## 🚀 已完成的修改与功能实现

根据 `GEMINI.md` 的规范，我已完成了以下工作：

1.  **项目架构搭建**：
    *   建立了标准的 Clean Architecture 目录结构 (`app/core`, `app/models`, `app/services`, `app/routers`)。
    *   配置了 `main.py` 作为程序入口。

2.  **核心数据模型 (`models/ui_protocol.py`)**：
    *   完整实现了 Generative UI 的协议。
    *   包含所有 10 种组件类型：`Input`, `Select`, `DatePicker`, `MultiSelect`, `Button`, `MapPin`, `RangeSlider`, `VisualPicker`, `Stepper`, `Switch`。

3.  **LLM 服务集成 (`services/llm.py`)**：
    *   实现了 `OpenAIService`。
    *   设计了 System Prompt，确保 LLM 能够输出符合 UI 协议的结构化 JSON 数据。

4.  **MCP (Model Context Protocol) 客户端 (`services/mcp_manager.py`)**：
    *   实现了 MCP 客户端服务，支持读取 `mcp_config.json` 配置。
    *   支持通过 Stdio 方式连接本地 MCP Server。

5.  **API 接口开发 (`routers/api.py`)**：
    *   `POST /api/v1/analyze`: 接收用户查询，返回动态 UI 结构。
    *   `POST /api/v1/execute`: 接收表单数据，规划并执行后续操作。

6.  **环境与配置**：
    *   修复并标准化了 `config.toml`。
    *   创建了 `mcp_config.json` 示例文件。
    *   使用 `uv` 管理依赖 (`fastapi`, `uvicorn`, `pydantic`, `openai`, `mcp` 等)。

## 🛠️ 如何运行

1.  **安装依赖**:
    ```bash
    uv sync
    ```

2.  **启动服务器**:
    ```bash
    python main.py
    # 或者
    uv run uvicorn app.main:app --reload
    ```

3.  **访问文档**:
    启动后访问: `http://localhost:8000/docs`
