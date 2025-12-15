from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The user input prompt.
            history: Optional list of message history [{'role': 'user', 'content': '...'}, ...].
            
        Returns:
            The generated text response.
        """
        pass
