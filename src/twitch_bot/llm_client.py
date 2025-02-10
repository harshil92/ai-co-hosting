"""Client for interacting with the LLM service."""
import aiohttp
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize the LLM client.
        
        Args:
            base_url: Base URL of the LLM service.
        """
        self.base_url = base_url
        
    async def is_available(self) -> bool:
        """Check if the LLM service is available.
        
        Returns:
            bool: True if the service is available and healthy.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("llm_available", False)
            return False
        except Exception as e:
            logger.error(f"Error checking LLM service health: {e}")
            return False
            
    async def generate_response(
        self,
        username: str,
        message: str,
        emotes: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Generate a response using the LLM service.
        
        Args:
            username: The username of the message sender.
            message: The content of the message.
            emotes: List of emotes used in the message.
            
        Returns:
            Optional[Dict]: Response data including generated text and context info,
                          or None if generation fails.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat",
                    json={
                        "username": username,
                        "message": message,
                        "emotes": emotes or []
                    }
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"LLM service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
            
    async def get_context(self) -> Optional[Dict]:
        """Get the current conversation context.
        
        Returns:
            Optional[Dict]: Context information or None if request fails.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/context") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error getting context: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return None 