from typing import Optional
from .base import BaseAIProvider
from .litellm_provider import LiteLLMProvider
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
        
        # We use LiteLLMProvider for 'gemini' and potentially other providers
        if provider_type == "gemini" or provider_type == "litellm":
            cls._instance = LiteLLMProvider(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_type}")
            
        return cls._instance
