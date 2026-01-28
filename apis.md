# API 接口文档

本项目后端提供两个核心 API 接口，分别用于**意图分析与UI生成**以及**任务执行**。

## 1. 意图分析与 UI 生成 (Analyze)

该接口接收用户的自然语言查询，分析其意图。如果信息缺失，它会返回一组 UI 组件定义；如果信息完整或只是闲聊，它会返回直接的文本回复。

- **URL**: `/api/v1/analyze`
- **Method**: `POST`
- **Content-Type**: `application/json`

### 请求参数 (Input)

| 字段名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `query` | string | 是 | 用户的自然语言输入，例如 "我想买台电脑" 或 "你好" |

**请求示例:**
```json
{
  "query": "我想买一台笔记本电脑，预算在5000左右"
}
```

### 响应参数 (Output)

返回一个符合 `UIResponse` 协议的 JSON 对象。

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `components` | array | UI 组件列表。如果为空，代表不需要用户输入更多信息。 |
| `message` | string | (可选) AI 的直接回复文本。通常当 `components` 为空时出现。 |

**响应示例 1：需要收集信息**
```json
{
  "components": [
    {
      "id": "usage",
      "label": "主要用途",
      "type": "Select",
      "options": [{"label":"办公","value":"office"}, {"label":"游戏","value":"gaming"}]
    }
  ],
  "message": null
}
```

**响应示例 2：直接回答**
```json
{
  "components": [],
  "message": "你好！我是你的智能助手，有什么可以帮你的吗？"
}
```

---

## 2. 任务执行 (Execute)

当用户在前端填写完 UI 组件的数据后，前端将原始查询和表单数据一起发送给此接口。后端将调用 MCP 工具（如搜索、API调用）来执行实际任务。

- **URL**: `/api/v1/execute`
- **Method**: `POST`
- **Content-Type**: `application/json`

### 请求参数 (Input)

| 字段名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `original_query` | string | 是 | 步骤1中用户的原始查询 |
| `form_data` | object | 是 | 用户在 UI 组件中填写的数据，键值对形式 (Key 为组件 ID) |

**请求示例:**
```json
{
  "original_query": "我想买一台笔记本电脑",
  "form_data": {
    "usage": "gaming",
    "budget": [5000, 8000],
    "os": "windows"
  }
}
```

### 响应参数 (Output)

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `result` | string | 执行结果的文本描述或总结 |

**响应示例:**
```json
{
  "result": "根据您的需求，推荐购买联想拯救者 Y9000P，配置..."
}
```

---

## 调试说明
项目启动后，可访问 Swagger UI 进行在线调试：
- 地址: `http://localhost:8000/docs`
