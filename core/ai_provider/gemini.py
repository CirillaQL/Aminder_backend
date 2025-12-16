from .base import BaseAIProvider
from typing import List, Dict, Any, Optional
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel

from google.genai import types
from google import genai


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model
        
        if not self.api_key:
            raise ValueError("API key must be provided for GeminiProvider.")
        
        self.client = genai.Client(api_key=self.api_key)
        
    def generate_response(self, prompt: str, web_search: bool = False) -> str | None:
        try:
            config = types.GenerateContentConfig()
            if web_search:
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                config = types.GenerateContentConfig(tools=[grounding_tool])

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
