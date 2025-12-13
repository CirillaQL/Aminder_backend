from typing import Optional
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from core.config import settings

class AIProviderFactory:
    _instance: Optional[BaseAIProvider] = None

    @classmethod
    def get_provider(cls) -> BaseAIProvider:
        if cls._instance:
            return cls._instance
            
        provider_type = settings.ai.provider.lower()
        api_key = settings.ai.api_key
        model = settings.ai.model
        
        if provider_type == "gemini":
            cls._instance = GeminiProvider(api_key=api_key, model=model)
        elif provider_type == "openai":
            cls._instance = OpenAIProvider(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_type}")
            
        return cls._instance
