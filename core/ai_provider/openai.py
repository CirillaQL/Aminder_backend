from .base import BaseAIProvider
from typing import List, Dict, Any

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        # TODO: Initialize OpenAI client here when SDK is added
        
    async def generate_response(self, prompt: str, history: List[Dict[str, str]] = None) -> str:
        # Placeholder implementation
        return f"OpenAI response to: {prompt} (Model: {self.model})"
