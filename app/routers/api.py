import json
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel

from app.core.database import Chat, Message, User
from app.models.ui_protocol import UIResponse
from app.services.auth import auth_service
from app.services.llm import OpenAIService
from app.services.mcp_manager import mcp_service

router = APIRouter()
llm_service = OpenAIService()


# --- Dependencies ---
async def get_current_user(authorization: str = Header(...)) -> User:
    """Validate token and return current user."""
    user = auth_service.verify_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


# --- Models ---
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_at: str


class ChatInfo(BaseModel):
    chatId: str
    title: str
    created_at: str


class HistoryItem(BaseModel):
    role: str
    content: Union[str, Dict[str, Any], UIResponse]
    created_at: str


class AnalyzeRequest(BaseModel):
    query: str
    chat_id: str


class ExecuteRequest(BaseModel):
    original_query: str
    form_data: Dict[str, Any]
    chat_id: str


# --- Endpoints ---
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    token = auth_service.login_or_register(request.username, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Get user to return expiry (simplified)
    user = User.get(User.token == token)
    return {"token": token, "expires_at": user.token_expires.isoformat()}


@router.get("/chatList", response_model=List[ChatInfo])
async def get_chat_list(user: User = Depends(get_current_user)):
    chats = Chat.select().where(Chat.user == user).order_by(Chat.created_at.desc())
    return [
        {"chatId": str(c.id), "title": c.title, "created_at": c.created_at.isoformat()}
        for c in chats
    ]


@router.post("/chat", response_model=ChatInfo)
async def create_chat(user: User = Depends(get_current_user)):
    """Create a new chat session."""
    chat = Chat.create(user=user, title="New Chat")
    return {
        "chatId": str(chat.id),
        "title": chat.title,
        "created_at": chat.created_at.isoformat(),
    }


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    range: Optional[str] = Query(None, description="Range like [1, 5]"),
    chat_id: str = Query(..., description="Chat ID is required"),
    user: User = Depends(get_current_user),
):
    try:
        chat = Chat.get((Chat.id == chat_id) & (Chat.user == user))
    except Chat.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Default range logic: [1, 5] (Latest 5 messages)
    start, end = 1, 5
    if range:
        try:
            # Parse [min, max]
            trimmed = range.strip("[]")
            parts = trimmed.split(",")
            if len(parts) == 2:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
        except Exception:
            pass  # Fallback to default

    # Convert 1-based range to limit/offset
    # range=[1, 5] means latest 1st to 5th message.
    # Logic: Order by DESC, limit = end - start + 1, offset = start - 1
    limit = end - start + 1
    offset = start - 1

    messages = (
        Message.select()
        .where(Message.chat == chat)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    # Reverse to return in chronological order if desired, or keep DESC.
    # Usually history is displayed top-to-bottom (oldest first) in UI,
    # but "recent 5" usually means [Latest, ..., 5th Latest].
    # Let's return them in chronological order for the slice requested.
    msgs_list = list(messages)
    msgs_list.reverse()

    result = []
    for m in msgs_list:
        content_val = m.content
        # Try to parse JSON content
        try:
            content_val = json.loads(m.content)
        except Exception:
            pass

        result.append(
            {
                "role": m.role,
                "content": content_val,
                "created_at": m.created_at.isoformat(),
            }
        )
    return result


@router.post("/analyze", response_model=UIResponse)
async def analyze_intent(
    request: AnalyzeRequest, user: User = Depends(get_current_user)
):
    try:
        # 1. Validate Chat Context
        try:
            chat = Chat.get((Chat.id == request.chat_id) & (Chat.user == user))
        except Chat.DoesNotExist:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Auto-update title for new chats
        if chat.title == "New Chat":
            new_title = (
                (request.query[:20] + "...")
                if len(request.query) > 20
                else request.query
            )
            chat.title = new_title
            chat.save()

        # 2. Save User Query
        Message.create(chat=chat, role="user", content=request.query)

        # 3. Fetch History for LLM (Last 10 messages for context)
        recent_msgs = (
            Message.select()
            .where(Message.chat == chat)
            .order_by(Message.created_at.desc())
            .offset(1)  # Skip the one we just added
            .limit(10)
        )

        history_context = []
        for m in reversed(list(recent_msgs)):
            history_context.append({"role": m.role, "content": m.content})

        # 4. Call LLM
        ui_response = llm_service.analyze_intent(request.query, history=history_context)

        # 5. Save Assistant Response
        Message.create(
            chat=chat, role="assistant", content=ui_response.model_dump_json()
        )

        return ui_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_request(
    request: ExecuteRequest, user: User = Depends(get_current_user)
):
    try:
        try:
            chat = Chat.get((Chat.id == request.chat_id) & (Chat.user == user))
        except Chat.DoesNotExist:
            raise HTTPException(status_code=404, detail="Chat not found")

        # 1. Fetch History
        # We do NOT save 'original_query' again as user message, per instructions.
        # We do NOT save 'form_data'.
        # We just need history to give LLM context.
        recent_msgs = (
            Message.select()
            .where(Message.chat == chat)
            .order_by(Message.created_at.desc())
            .limit(10)
        )

        history_context = []
        for m in reversed(list(recent_msgs)):
            history_context.append({"role": m.role, "content": m.content})

        # 2. Call LLM
        tools_desc = await mcp_service.get_available_tools()
        result = llm_service.plan_execution(
            request.original_query,
            request.form_data,
            tools_desc,
            history=history_context,
        )

        # 3. Save Assistant Result
        Message.create(chat=chat, role="assistant", content=result)

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
