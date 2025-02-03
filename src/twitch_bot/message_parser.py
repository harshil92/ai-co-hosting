"""Message parser for processing Twitch chat messages."""
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

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
        
    def parse_message(self, message: Dict) -> Optional[ParsedMessage]:
        """Parse a raw chat message into a structured format.
        
        Args:
            message: Raw message data from Twitch chat
            
        Returns:
            ParsedMessage object if message should be processed, None if message should be ignored
        """
        content = message.get('content', '').strip()
        author = message.get('author', '').lower()
        
        # Ignore empty messages
        if not content:
            return None
            
        # Check if message is a command
        is_command = content.startswith('!')
        if is_command:
            return None  # Ignore commands
            
        # Extract mentioned users (including @mentions)
        mentioned_users = [
            user.lower() for user in re.findall(r'@(\w+)', content)
        ]
        
        # Check if message is addressed to the bot
        addressed_to_bot = (
            self.bot_username in mentioned_users or
            content.lower().startswith(self.bot_username)
        )
        
        # Extract potential emotes (simple pattern matching)
        emotes = self.emote_pattern.findall(content)
        
        # Check if message is a question
        is_question = bool(self.question_pattern.match(content))
        
        return ParsedMessage(
            content=content,
            author=author,
            timestamp=message.get('timestamp', datetime.now().isoformat()),
            is_command=is_command,
            mentioned_users=mentioned_users,
            emotes=emotes,
            is_question=is_question,
            addressed_to_bot=addressed_to_bot,
            raw_message=message
        )
    
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