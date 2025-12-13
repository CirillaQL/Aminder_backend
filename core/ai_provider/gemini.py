from .base import BaseAIProvider
from typing import List, Dict, Any
import google.generativeai as genai

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
    async def generate_response(self, prompt: str, history: List[Dict[str, str]] = None) -> str:
        try:
            # TODO: Better handling of history if provided using start_chat
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

