"""Message parser for processing Twitch chat messages."""
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParsedMessage:
    """Structured representation of a parsed chat message."""
    content: str
    author: str
    timestamp: str
    is_command: bool
    mentioned_users: List[str]
    emotes: List[str]
    is_question: bool
    addressed_to_bot: bool
    raw_message: Dict

class MessageParser:
    """Parser for Twitch chat messages."""
    
    def __init__(self, bot_username: str):
        """Initialize the parser.
        
        Args:
            bot_username: The bot's Twitch username to detect when it's mentioned
        """
        self.bot_username = bot_username.lower()
        # Common Twitch emote patterns
        self.emote_pattern = re.compile(r'[A-Z]\w+')
        # Question patterns
        self.question_pattern = re.compile(r'^(?:who|what|when|where|why|how|is|are|can|could|would|will|do|does|did|should|may|might)\b.*\?$', re.IGNORECASE)
        
    def should_respond(self, message: str) -> bool:
        """Determine if the bot should respond to a message.
        
        Args:
            message: The message content to check
            
        Returns:
            bool: True if the bot should respond, False otherwise
        """
        message = message.lower().strip()
        
        # Always respond to direct commands
        if message.startswith('!'):
            return True
            
        # Respond if bot is not mentioned or 
        if not self.bot_username in message or f'@{self.bot_username}' in message:
            return True
            
        # Respond to direct questions
        if self.question_pattern.match(message):
            return True
            
        # Don't respond to messages that are too short or seem like chat noise
        if len(message.split()) < 2:
            return False
            
        # Log the decision for debugging
        logger.debug(f"Should respond to message '{message}': {False}")
        return False
        
    def parse_message(self, message_data: Dict) -> Optional[ParsedMessage]:
        """Parse a message and determine if it's addressed to the bot."""
        try:
            content = message_data['content'].strip()
            author = message_data['author']
            
            # Check if message mentions bot's username
            addressed_to_bot = (
                self.bot_username.lower() in content.lower() or
                content.startswith('!') or  # Consider commands as addressed to bot
                content.startswith('@' + self.bot_username.lower())
            )
            
            # Extract any @mentions
            mentioned_users = re.findall(r'@(\w+)', content)
            
            # Simple question detection
            is_question = '?' in content
            
            # Extract emotes if present
            emotes = message_data.get('emotes', [])
            
            logger.debug(f"Parsed message - addressed_to_bot: {addressed_to_bot}, " 
                        f"author: {author}, content: {content}")
            
            return ParsedMessage(
                content=content,
                author=author,
                timestamp=message_data.get('timestamp', datetime.now().isoformat()),
                is_command=content.startswith('!'),
                mentioned_users=mentioned_users,
                emotes=emotes,
                is_question=is_question,
                addressed_to_bot=addressed_to_bot,
                raw_message=message_data
            )
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def format_for_dialogue(self, parsed_message: ParsedMessage) -> Dict:
        """Format a parsed message for the dialogue engine.
        
        Args:
            parsed_message: The parsed message to format
            
        Returns:
            Dict containing formatted message data for the dialogue engine
        """
        return {
            "role": "user",
            "author": parsed_message.author,
            "content": parsed_message.content,
            "metadata": {
                "timestamp": parsed_message.timestamp,
                "is_question": parsed_message.is_question,
                "addressed_to_bot": parsed_message.addressed_to_bot,
                "mentioned_users": parsed_message.mentioned_users,
                "emotes": parsed_message.emotes
            }
        } 