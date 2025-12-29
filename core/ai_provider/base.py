from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, history: List[Dict[str, Any]] = None, system_instruction: str = None, web_search: bool = False) -> str | None:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The user input prompt.
            history: Optional list of message history [{'role': 'user', 'content': '...'}, ...].
            system_instruction: Optional system instruction/prompt.
            web_search: Whether to enable web search.
            
        Returns:
            The generated text response.
        """
        pass