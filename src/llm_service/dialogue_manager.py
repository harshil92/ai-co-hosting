from typing import List, Dict, Optional, Set
from collections import deque
from datetime import datetime, timedelta
import json
from .llm_client import LMStudioClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DialogueManager:
    def __init__(self, llm_client: LMStudioClient):
        """Initialize the dialogue manager.
        
        Args:
            llm_client: The LLM client instance to use for generating responses.
        """
        self.llm_client = llm_client
        self.context: List[Dict] = []
        self.metadata = {
            "context_summary": "",
            "current_topics": set(),
            "last_update": datetime.utcnow().isoformat()
        }
        self.max_context_length = 10
        self.system_prompt = (
            "You are a friendly and engaging Twitch chat co-host. "
            "Keep responses concise, natural, and engaging. "
            "Maintain conversation flow and topic relevance."
        )
    
    def _update_metadata(self):
        """Update the conversation metadata."""
        self.metadata["last_update"] = datetime.utcnow().isoformat()
        
        # Extract topics from recent messages
        topics = set()
        for msg in self.context[-3:]:  # Look at last 3 messages
            if msg["role"] == "user":
                # Add basic topic extraction logic here
                words = msg["content"].lower().split()
                # Filter common words and keep potential topics
                topics.update(word for word in words if len(word) > 3)
        
        self.metadata["current_topics"] = topics
    
    def _trim_context(self):
        """Trim the context to maintain the maximum length."""
        if len(self.context) > self.max_context_length:
            # Keep system message and trim oldest messages
            system_msg = next((msg for msg in self.context if msg["role"] == "system"), None)
            self.context = self.context[-self.max_context_length:]
            if system_msg and system_msg not in self.context:
                self.context.insert(0, system_msg)
    
    def add_message(self, username: str, message: str, emotes: Optional[List[str]] = None):
        """Add a message to the conversation context.
        
        Args:
            username: The username of the message sender
            message: The message content
            emotes: Optional list of emotes used in the message
        """
        try:
            # Format the message with username and emotes
            formatted_message = f"{username}: {message}"
            if emotes:
                formatted_message += f" [emotes: {', '.join(emotes)}]"
            
            # Add to context
            self.context.append({
                "role": "user",
                "content": formatted_message,
                "metadata": {
                    "username": username,
                    "timestamp": datetime.utcnow().isoformat(),
                    "emotes": emotes or []
                }
            })
            
            self._trim_context()
            self._update_metadata()
            
        except Exception as e:
            logger.error(f"Error adding message to context: {str(e)}")
            raise
    
    async def generate_response(self) -> Optional[str]:
        """Generate a response based on the current context.
        
        Returns:
            The generated response text or None if generation fails.
        """
        try:
            # Ensure system prompt is present
            if not self.context or self.context[0]["role"] != "system":
                self.context.insert(0, {
                    "role": "system",
                    "content": self.system_prompt
                })
            
            # Generate response
            response = await self.llm_client.generate_response(
                messages=self.context,
                temperature=0.7,  # Balanced between consistency and creativity
                top_p=0.95
            )
            
            if response:
                # Add response to context
                self.context.append({
                    "role": "assistant",
                    "content": response,
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
                
                self._trim_context()
                self._update_metadata()
                
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None
    
    def get_context_info(self) -> Dict:
        """Get detailed information about the current conversation context.
        
        Returns:
            Dictionary containing context, metadata, and system prompt.
        """
        return {
            "context": self.context,
            "metadata": {
                **self.metadata,
                "current_topics": list(self.metadata["current_topics"])
            },
            "system_prompt": self.system_prompt
        } 