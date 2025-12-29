from typing import Optional, List, Dict, Any
import litellm
from .base import BaseAIProvider

class LiteLLMProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        
        if not self.api_key:
            raise ValueError("API key must be provided for LiteLLMProvider.")

    async def generate_response(self, prompt: str, history: List[Dict[str, Any]] = None, system_instruction: str = None, web_search: bool = False) -> str | None:
        """
        Generates a response using LiteLLM asynchronously.
        """
        messages = []
        
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
            
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": prompt})
        
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "api_key": self.api_key
        }

        if web_search:
            # Configure Google Search tool for LiteLLM
            tools = [{
                "google_search": {}
            }]
            params["tools"] = tools

        try:
            # Use acompletion for async execution
            response = await litellm.acompletion(**params)
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            return None
            
        except Exception as e:
            # Log the error properly in a real app
            print(f"Error calling LiteLLM: {str(e)}")
            return f"Error calling AI Provider: {str(e)}"