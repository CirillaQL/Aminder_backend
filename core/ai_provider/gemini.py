from .base import BaseAIProvider
from typing import List, Dict, Any, Optional
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model
        configure(api_key=self.api_key)
        self.model = GenerativeModel(self.model_name)
        
    async def generate_response(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        try:
            # TODO: Better handling of history if provided using start_chat
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
