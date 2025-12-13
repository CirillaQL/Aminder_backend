from fastapi import APIRouter, HTTPException, Depends
from .schemas import ChatRequest, ChatResponse
from .service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_chat_service():
    return ChatService()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, service: ChatService = Depends(get_chat_service)):
    try:
        response_text = await service.chat(request.message, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
