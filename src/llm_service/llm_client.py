import os
import json
import requests
import re
from typing import List, Dict, Optional

class LMStudioClient:
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        """Initialize the LM Studio client.
        
        Args:
            base_url: The base URL of the LM Studio server. Defaults to localhost:1234.
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _clean_response(self, text: str) -> str:
        """Clean the response text by removing internal monologue and extra whitespace.
        
        Args:
            text: Raw response text from the LLM.
            
        Returns:
            Cleaned response text.
        """
        # Remove <think>...</think> blocks
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # Remove thought process patterns
        thought_patterns = [
            # Original patterns
            r'Alright,\s*I\s*just\s*got\s*a\s*message.*?saying,\s*"|So,\s*they\'re\s*greeting\s*me.*?\.', 
            r'I\s*need\s*to\s*respond.*?\.', 
            r'First,\s*I\s*should.*?\.', 
            r'Maybe\s*start\s*with.*?\.', 
            r'Then,\s*(?:I\s*should|address).*?\.', 
            r'Next,\s*I\s*should.*?\.', 
            r'That\s*way.*?\.', 
            r'Since\s*I\s*don\'t\s*have\s*feelings.*?\.',
            # New patterns
            r'Okay,\s*so\s*I\'m\s*trying\s*to\s*figure\s*out.*?\.', 
            r'The\s*user\s*sent\s*a\s*message\s*saying.*?and\s*the\s*response.*?\.', 
            r'Hmm,\s*let\'s\s*break\s*this\s*down.*?\.', 
            r'(?:Okay|Alright|Well|So),\s*(?:let\'s|I\'m|I\'ll).*?\.', 
            r'I\s*(?:think|believe|feel|should).*?\.', 
            r'Let\s*me.*?\.', 
            r'(?:First|Then|Next|Finally),.*?\.', 
            r'As\s*(?:a|an|the)\s*(?:AI|co-host|assistant).*?\.', 
            r'My\s*role\s*is.*?\.'
        ]
        
        for pattern in thought_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove any remaining XML-like tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up quotation marks and whitespace
        text = re.sub(r'"{2,}', '"', text)  # Remove multiple quotes
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # If the text starts with a quote, clean it up
        if text.startswith('"') and text.count('"') == 1:
            text = text[1:]
        
        # Remove any remaining quoted text that looks like example responses
        text = re.sub(r'"[^"]*?"(?:\s*and|\s*or|\s*but)?', '', text)
        
        # Clean up any leftover artifacts
        text = re.sub(r'^\s*(?:and|or|but)\s+', '', text)
        text = text.strip()
        
        return text
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> Optional[str]:
        """Generate a response using the LM Studio API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 to 1.0).
            top_p: Top-p sampling parameter.
            
        Returns:
            Generated text response or None if the request fails.
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"response: {result}")
                raw_response = result["choices"][0]["message"]["content"]
                cleaned_response = self._clean_response(raw_response)
                
                # Ensure the response isn't cut off
                if cleaned_response.endswith(('...', ',', '. ', '! ', '? ')):
                    cleaned_response = cleaned_response.rstrip('.!?, ')
                
                return cleaned_response
            else:
                print(f"Error: API request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None
            
    async def get_response(self, message: str) -> Optional[str]:
        """Get a response for a chat message.
        
        Args:
            message: The chat message to respond to
            
        Returns:
            Generated response text or None if generation fails
        """
        messages = [
            {"role": "system", "content": "You are a friendly and engaging Twitch chat co-host. Keep responses concise and natural."},
            {"role": "user", "content": message}
        ]
        
        return self.generate_response(messages)
            
    def is_available(self) -> bool:
        """Check if the LM Studio server is available.
        
        Returns:
            True if the server is responding, False otherwise.
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False 