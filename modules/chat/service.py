from core.ai_provider import AIProviderFactory
from typing import List, Dict
from .schemas import Message

class ChatService:
    def __init__(self):
        self.provider = AIProviderFactory.get_provider()

    async def chat(self, message: str, history: List[Message] = None) -> str:
        # Convert Pydantic models to dicts for the provider if necessary, 
        # or update provider to accept Pydantic models. 
        # For now, let's assume the provider expects a list of dicts.
        history_dicts = [h.model_dump() for h in history] if history else []
        
        response = await self.provider.generate_response(prompt=message, history=history_dicts)
        return response
