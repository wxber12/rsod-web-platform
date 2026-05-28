from fastapi import APIRouter, HTTPException
from app.services.ai_service import chat_with_deepseek
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = await chat_with_deepseek(request.question, request.history)
        return ChatResponse(
            success=True,
            message="Success",
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
