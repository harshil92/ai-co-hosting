from typing import List, Dict, Optional, Set
from collections import deque
from datetime import datetime, timedelta
import json
from .llm_client import LMStudioClient

class DialogueManager:
    def __init__(self, context_length: int = 5):
        """Initialize the dialogue manager.
        
        Args:
            context_length: Number of previous messages to keep in context.
        """
        self.llm_client = LMStudioClient()
        self.context = deque(maxlen=context_length)
        self.metadata = {
            "total_messages": 0,
            "unique_users": set(),
            "last_interaction": None,
            "context_summary": None,
            "current_topics": set(),  # Track conversation topics
            "emotes_used": {},  # Track emote usage frequency
            "active_users": {},  # Track user activity timestamps
            "mentioned_users": set(),  # Track mentioned users
            "conversation_start": datetime.utcnow().isoformat()
        }
        self._update_system_prompt()
    
    def _update_system_prompt(self):
        """Update the system prompt with current context and metadata."""
        base_prompt = (
            "You are a friendly and engaging Twitch co-host. Respond directly to messages without any meta-commentary. "
            "Keep responses concise (1-2 sentences), entertaining, and suitable for a live stream. "
            "Never explain your thought process or how you plan to respond. "
            "Never quote example responses. Just give your actual response naturally. "
            "Match the chat's energy and use emotes when appropriate. "
            "If chat is using specific emotes, consider using them in your response too."
        )
        
        # Add context information
        context_info = ""
        if self.metadata["context_summary"]:
            context_info = f"\nCurrent conversation context: {self.metadata['context_summary']}"
        
        # Add topic information
        if self.metadata["current_topics"]:
            topics = ", ".join(self.metadata["current_topics"])
            context_info += f"\nCurrent topics: {topics}"
        
        # Add popular emotes
        if self.metadata["emotes_used"]:
            top_emotes = sorted(
                self.metadata["emotes_used"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            if top_emotes:
                emotes = ", ".join(emote for emote, _ in top_emotes)
                context_info += f"\nPopular emotes: {emotes}"
            
        # Add chat stats
        active_users = len([
            user for user, last_seen in self.metadata["active_users"].items()
            if (datetime.utcnow() - datetime.fromisoformat(last_seen)) < timedelta(minutes=5)
        ])
        
        stats_info = (
            f"\nStream stats: {active_users} active chatters, "
            f"{len(self.metadata['unique_users'])} unique chatters, "
            f"{self.metadata['total_messages']} total messages"
        )
        
        self.system_prompt = f"{base_prompt}{context_info}{stats_info}"
    
    def _update_context_summary(self):
        """Update the context summary based on recent messages."""
        if not self.context:
            self.metadata["context_summary"] = None
            return
            
        # Create a summary prompt for the LLM
        summary_messages = [
            {
                "role": "system",
                "content": (
                    "Summarize the following Twitch chat conversation in one brief sentence. "
                    "Focus on the main topic, mood, and any recurring themes or memes. "
                    "If there are popular emotes being used, mention them."
                )
            },
            {
                "role": "user",
                "content": "\n".join([msg["content"] for msg in self.context])
            }
        ]
        
        summary = self.llm_client.generate_response(
            messages=summary_messages,
            max_tokens=50,
            temperature=0.5
        )
        
        self.metadata["context_summary"] = summary
    
    def _extract_topics(self, message: str) -> Set[str]:
        """Extract potential topics from a message using the LLM."""
        topic_messages = [
            {
                "role": "system",
                "content": (
                    "Extract 1-2 main topics from this Twitch chat message. "
                    "Return only the topics as a comma-separated list. "
                    "Topics should be 1-2 words each. If no clear topics, return 'general chat'."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]
        
        response = self.llm_client.generate_response(
            messages=topic_messages,
            max_tokens=30,
            temperature=0.3
        )
        
        if response:
            return {topic.strip().lower() for topic in response.split(",")}
        return {"general chat"}
    
    def _update_emote_stats(self, emotes: List[str]) -> None:
        """Update emote usage statistics."""
        for emote in emotes:
            self.metadata["emotes_used"][emote] = (
                self.metadata["emotes_used"].get(emote, 0) + 1
            )
    
    def add_message(self, username: str, message: str, emotes: Optional[List[str]] = None) -> None:
        """Add a new message to the context.
        
        Args:
            username: The Twitch username of the message sender.
            message: The content of the message.
            emotes: List of emotes used in the message.
        """
        # Update metadata
        self.metadata["total_messages"] += 1
        self.metadata["unique_users"].add(username)
        self.metadata["active_users"][username] = datetime.utcnow().isoformat()
        
        # Update emote stats if provided
        if emotes:
            self._update_emote_stats(emotes)
        
        # Extract and update topics
        new_topics = self._extract_topics(message)
        self.metadata["current_topics"].update(new_topics)
        
        # Keep only the 5 most recent topics
        self.metadata["current_topics"] = set(
            list(self.metadata["current_topics"])[-5:]
        )
        
        # Add message to context
        self.context.append({
            "role": "user",
            "content": f"{username}: {message}",
            "timestamp": datetime.utcnow().isoformat(),
            "emotes": emotes or []
        })
        
        # Update context summary every few messages
        if self.metadata["total_messages"] % 3 == 0:
            self._update_context_summary()
        
        # Always update the system prompt with new information
        self._update_system_prompt()
    
    def generate_response(self) -> str:
        """Generate a response based on the current context.
        
        Returns:
            Generated response text, or an error message if generation fails.
        """
        if not self.llm_client.is_available():
            return "Sorry, I'm having trouble connecting to my brain right now!"
            
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(list(self.context))
        
        response = self.llm_client.generate_response(
            messages=messages,
            max_tokens=100,  # Keep responses concise
            temperature=0.7  # Balance between creativity and coherence
        )
        
        if response:
            # Add the response to the context
            self.context.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })
            return response
        else:
            return "I'm having trouble thinking of a response right now!"
    
    def get_context_info(self) -> Dict:
        """Get detailed information about the current context.
        
        Returns:
            Dictionary containing context and metadata information.
        """
        # Clean up old topics and users
        self._cleanup_metadata()
        
        return {
            "context": list(self.context),
            "metadata": {
                **self.metadata,
                "unique_users": list(self.metadata["unique_users"]),
                "current_topics": list(self.metadata["current_topics"]),
                "mentioned_users": list(self.metadata["mentioned_users"])
            },
            "system_prompt": self.system_prompt
        }
    
    def _cleanup_metadata(self) -> None:
        """Clean up old metadata entries."""
        now = datetime.utcnow()
        
        # Remove inactive users (not seen in last 10 minutes)
        self.metadata["active_users"] = {
            user: timestamp
            for user, timestamp in self.metadata["active_users"].items()
            if (now - datetime.fromisoformat(timestamp)) < timedelta(minutes=10)
        }
        
        # Limit emotes to top 10
        if len(self.metadata["emotes_used"]) > 10:
            sorted_emotes = sorted(
                self.metadata["emotes_used"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            self.metadata["emotes_used"] = dict(sorted_emotes) 