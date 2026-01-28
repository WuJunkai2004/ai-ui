from openai import OpenAI
import json
from app.core.config import settings
from app.models.ui_protocol import UIResponse

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.api_base,
            api_key=settings.api_key
        )
        self.model = settings.model

    def analyze_intent(self, query: str) -> UIResponse:
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                # response_format={"type": "json_object"} # Uncomment if supported by provider
            )
            
            content = response.choices[0].message.content
            print(f"DEBUG: Raw LLM content: {content!r}")

            if not content:
                raise ValueError("LLM returned empty content")

            # 1. Strip <think> tags (common in reasoning models)
            import re
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            
            # 2. Extract JSON from Markdown code blocks if present
            code_block_match = re.search(r"```json\s*(\{.*\})\s*```", content, re.DOTALL)
            if code_block_match:
                content = code_block_match.group(1)
            else:
                # 3. Fallback: Find the first outer-most JSON object
                # This regex looks for a starting { and tries to match until the end, 
                # but cleaning the string first is usually safer.
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
            
            print(f"DEBUG: Cleaned content for parsing: {content!r}")
            data = json.loads(content)
            return UIResponse(**data)
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            # Fallback or re-raise
            raise e

    def plan_execution(self, original_query: str, form_data: dict, tools_desc: str) -> str:
        system_prompt = f"""
        You are an orchestration agent. You have access to the following MCP tools:
        {tools_desc}
        
        The user wants: {original_query}
        They provided the following details: {json.dumps(form_data)}
        
        Decide which tool to call and with what arguments. 
        For this prototype, return a text description of the plan or the tool call you would make.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Execute the request."}
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        return response.choices[0].message.content
