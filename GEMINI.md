# Project Specification: GenUI-Agent-Backend

## 1. Project Overview
We are building an AI Agent backend that bridges the gap between vague user intents and precise execution.
**Core Philosophy:** Users cannot always prompt perfectly. The system interprets vague requests, generates a dynamic, structured UI (Generative UI) to collect missing data, and then executes tasks using the Model Context Protocol (MCP).
The project is done in Python using FastAPI and OpenAI's LLMs, with MCP for tool integration.

## 2. Tech Stack & Environment
- **Language:** Python 3.10+
- **Package Manager:** `uv`
- **Web Framework:** FastAPI
- **LLM Provider:** OpenAI API (gpt-4o or compatible)
- **Core Protocol:** MCP (Model Context Protocol) - Python SDK
- **Architecture pattern:** Clean Architecture / Service-Repository pattern.

## 3. Core Workflow (The "Three-Step Loop")

### Step 1: Clarification (Intent Analysis)
- Input: User's natural language query (e.g., "Plan a trip to SF").
- Process: LLM analyzes the query to identify missing information.
- Output: A structured JSON Schema defining specific UI components to render on the frontend.

### Step 2: Information Collection (Frontend - Out of Scope for now, but Backend must support it)
- The frontend renders the components defined in Step 1.
- User interacts and submits structured data.

### Step 3: Execution (Orchestration)
- Input: The structured data from Step 2 combined with original intent.
- Process: The Backend acts as an **MCP Host**. It connects to available MCP Servers (e.g., Tools for Search, Maps, Booking).
- Action: The LLM plans the execution path and calls MCP tools.
- Output: Final result to the user.

## 4. Detailed Data Structures (Pydantic Models)

### 4.0 The AI configuration
The configuration for the AI model and MCP integration is defined in `./config.toml`, You can read it directly using `tomli` package.

### 4.1 The UI Protocol
We need a robust Pydantic model system to define the Generative UI elements. The `UIResponse` should contain a list of components.
Supported Component Types:
1.  `Input` (text fields)
2.  `Select` (dropdowns)
3.  `DatePicker` (or DateRangePicker)
4.  `MultiSelect` (tags)
5.  `Button` (confirmation/actions)
6.  `MapPin` (location selection)
7.  `RangeSlider` (for budgets, duration - `[min, max]`)
8.  `VisualPicker` (for style preference - contains image URLs and values)
9.  `Stepper` (for counts like number of people)
10. `Switch` (boolean toggles)

### 4.2 API Request/Response
- `POST /api/v1/analyze`: Accepts `{ "query": str }`. Returns `UIResponse`.
- `POST /api/v1/execute`: Accepts `{ "original_query": str, "form_data": Dict[str, Any] }`. Returns final execution result.

## 5. MCP Integration (Crucial)
- The application acts as an **MCP Client/Host**.
- It needs a `MCPSessionManager` service.
- It should be able to connect to local MCP servers via Stdio (Standard Input/Output).
- **Configuration:** Use a simple `mcp_config.json` or `.env` to define which MCP servers to launch (command + args).
- **Tool Use:** The OpenAI client must be configured to see the tools exposed by the connected MCP servers.

## 6. Development Guidelines
- Use `pydantic` for all data validation.
- Use `fastapi.APIRouter` to structure endpoints.
- Ensure the OpenAI API key is loaded from environment variables.
- Create a dummy/mock MCP server tool logic if no real MCP server is connected yet, but the architecture must support real MCP connections.