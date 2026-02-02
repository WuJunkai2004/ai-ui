import json
import re

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_tool_union_param import (
    ChatCompletionToolUnionParam,
)
from starlette.types import Message

from app.core.config import settings
from app.core.logging import logger
from app.models.ui_protocol import UIResponse
from app.services.mcp_manager import mcp_service


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(base_url=settings.api_base, api_key=settings.api_key)
        self.model = settings.model

    async def analyze_intent(
        self,
        query: str,
        history: list[ChatCompletionMessageParam] = None,  # type: ignore
    ) -> UIResponse:
        system_prompt = """
        You are an expert AI Assistant capable of generating dynamic UIs.
        Your goal is to analyze the user's request.

        1. If the user's request is vague or requires parameters to execute a task, output a list of UI 'components' to collect this data.
        2. If the request is a greeting, a simple question, or fully specified, provide a direct answer in the 'message' field and return an empty 'components' list.

        You must output a JSON object strictly following the UI Protocol schema.

        Supported types: Input, Select, DatePicker, MultiSelect, Button, MapPin, RangeSlider, VisualPicker, Stepper, Switch.
        IMPORTANT: For 'Select' and 'MultiSelect', the 'options' field must be a list of objects with 'label' and 'value' keys.

        Example (Components needed):
        {"components":[{"id":"budget","type":"RangeSlider","label":"Budget","min":0,"max":1000,"unit":"USD"}]}

        Example (Direct Answer):
        {"components":[],"message":"Hello! How can I help you today?"}

        Constraint: Output compact JSON without unnecessary whitespace to save tokens. Do not add markdown formatting.
        """

        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt}
            ]
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": query})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                # response_format={"type": "json_object"} # Uncomment if supported by provider
            )

            if not response.choices:
                if hasattr(response, "error_message") and getattr(
                    response, "error_message"
                ):
                    error_msg = f"Provider Error: {getattr(response, 'error_message')} (Code: {getattr(response, 'error_code', 'Unknown')})"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                logger.error(f"LLM Response has no choices: {response}")
                raise ValueError("LLM returned no choices")

            content = response.choices[0].message.content

            if not content:
                raise ValueError("LLM returned empty content")

            content = re.sub(
                r"<think>.*?</think>", "", content, flags=re.DOTALL
            ).strip()

            # 2. Extract JSON from Markdown code blocks if present
            code_block_match = re.search(
                r"```json\s*(\{.*\})\s*```", content, re.DOTALL
            )
            if code_block_match:
                content = code_block_match.group(1)
            else:
                # 3. Fallback: Find the first outer-most JSON object
                # This regex looks for a starting { and tries to match until the end,
                # but cleaning the string first is usually safer.
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)

            logger.debug(f"DEBUG: Cleaned content for parsing: {content!r}")
            data = json.loads(content)
            return UIResponse(**data)

        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            # Fallback or re-raise
            raise e

    async def plan_execution(
        self,
        original_query: str,
        form_data: dict,
        history: list[ChatCompletionMessageParam] = None,  # type: ignore
    ) -> str:
        # Get tools from MCP
        tools: list[ChatCompletionToolUnionParam] = await mcp_service.get_openai_tools()

        system_prompt = f"""
        You are an orchestration agent.
        The user wants: {original_query}
        They provided the following details: {json.dumps(form_data)}

        You have access to a set of tools. Use them to fulfill the user's request.
        If you need to search or perform actions, CALL THE TOOLS. Do not just describe what you will do.
        Once you have the information or performed the action, provide a final answer to the user.
        """

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]

        # Add history if provided (excluding the latest turn which is handled by system prompt context)
        # Note: In plan_execution, 'original_query' is essentially the user's last message.
        # But since we provide form_data and intent in system prompt, strictly speaking
        # the history helps provide context of *prior* turns.
        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": "Execute the request based on the provided details. Use tools if necessary.",
            }
        )

        max_turns = 30
        for _ in range(max_turns):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else [],
                tool_choice="auto" if tools else [],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
            )

            message = response.choices[0].message
            messages.append(message)

            # Check if there are tool calls
            if message.tool_calls and hasattr(message.tool_calls, "function"):
                logger.info(f"LLM requested {len(message.tool_calls)} tool calls")
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    logger.info(
                        f"Executing tool: {function_name} with args: {arguments}"
                    )

                    try:
                        # Call MCP Service
                        result = await mcp_service.execute_tool(
                            function_name, arguments
                        )
                        # Format result as string for LLM
                        content = str(result)
                        # Optional: limit result length if too huge
                        if len(content) > 5000:
                            content = content[:5000] + "...(truncated)"
                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        content = f"Error executing tool {function_name}: {e}"

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": content,
                        }
                    )
            else:
                # No tool calls, meaning the model produced a final response
                return message.content or ""

        return "Execution stopped (max turns reached) without final answer."
