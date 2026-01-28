from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.llm import OpenAIService
from app.services.mcp_manager import mcp_service
from app.models.ui_protocol import UIResponse

router = APIRouter()
llm_service = OpenAIService()

class AnalyzeRequest(BaseModel):
    query: str

class ExecuteRequest(BaseModel):
    original_query: str
    form_data: Dict[str, Any]

@router.post("/analyze", response_model=UIResponse)
async def analyze_intent(request: AnalyzeRequest):
    try:
        ui_response = llm_service.analyze_intent(request.query)
        return ui_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_request(request: ExecuteRequest):
    try:
        tools_desc = await mcp_service.get_available_tools()
        result = llm_service.plan_execution(request.original_query, request.form_data, tools_desc)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
