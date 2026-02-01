import json
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any, Dict

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import settings
from app.core.logging import logger

# Load environment variables from .env file
load_dotenv()


class MCPClientService:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.tools_map: Dict[
            str, Dict[str, Any]
        ] = {}  # tool_name -> {server_name, tool_obj}

    async def load_config_and_connect(self):
        """
        Reads mcp_config.json and connects to all defined servers.
        """
        config_path = settings.mcp_config_path
        if not os.path.exists(config_path):
            logger.warning(
                f"MCP config not found at {config_path}, skipping MCP connection."
            )
            return

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})

        for name, srv_conf in servers.items():
            if name in self.sessions:
                continue  # Already connected

            command = srv_conf.get("command")
            args = srv_conf.get("args", [])
            env = srv_conf.get("env", {})

            # Resolve command path (important for Windows)
            # shutil.which finds the full path of the executable
            resolved_command = shutil.which(command)
            if not resolved_command:
                # Fallback specific for npx on Windows if shutil.which didn't find it directly
                if command == "npx" and os.name == "nt":
                    resolved_command = shutil.which("npx.cmd")

                if not resolved_command:
                    logger.warning(
                        f"Warning: Command '{command}' not found in PATH for server '{name}'."
                    )
                    # We continue anyway, hoping the system can resolve it or it's an absolute path
                    resolved_command = command

            # Process environment variables: replace placeholders like ${VAR}
            processed_env = {}
            for k, v in env.items():
                if isinstance(v, str):
                    # expandvars replaces ${VAR} or $VAR with the value from os.environ
                    processed_env[k] = os.path.expandvars(v)
                else:
                    processed_env[k] = v

            # Merge with current env
            full_env = os.environ.copy()
            full_env.update(processed_env)

            server_params = StdioServerParameters(
                command=resolved_command, args=args, env=full_env
            )

            try:
                # Enter the stdio_client context
                transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                read, write = transport

                # Create and enter the session context
                session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )

                # Initialize
                await session.initialize()

                self.sessions[name] = session
                logger.info(f"Successfully connected to MCP Server: {name}")

            except Exception as e:
                logger.error(f"Failed to connect to MCP Server {name}: {e}")

    async def get_available_tools(self) -> str:
        """
        Lists all tools from all connected servers and returns a formatted string description.
        Also caches the mapping of tool_name -> server for execution.
        """
        if not self.sessions:
            await self.load_config_and_connect()

        self.tools_map.clear()
        descriptions = []

        for server_name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                for tool in result.tools:
                    self.tools_map[tool.name] = {"server": server_name, "tool": tool}

                    # Format description for LLM
                    desc = f"- {tool.name}: {tool.description}"
                    if tool.inputSchema:
                        desc += f"\n  Schema: {json.dumps(tool.inputSchema)}"
                    descriptions.append(desc)

            except Exception as e:
                logger.error(f"Error listing tools for {server_name}: {e}")

        if not descriptions:
            return "No tools available."

        return "\n".join(descriptions)

    async def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Executes a specific tool on the appropriate server.
        """
        if tool_name not in self.tools_map:
            raise ValueError(f"Tool '{tool_name}' not found.")

        server_name = self.tools_map[tool_name]["server"]
        session = self.sessions.get(server_name)

        if not session:
            raise ValueError(f"Session for server '{server_name}' is not active.")

        logger.info(f"Executing tool '{tool_name}' on server '{server_name}'.")
        result = await session.call_tool(tool_name, arguments)
        return result

    async def cleanup(self):
        await self.exit_stack.aclose()


# Singleton instance
mcp_service = MCPClientService()
