"""Command handlers for the Twitch bot."""
import logging
from typing import Optional
from twitchio.ext import commands

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, bot):
        self.bot = bot

    async def handle_tts_command(self, ctx: commands.Context, text: Optional[str] = None) -> None:
        """Handle the !tts command.
        
        Args:
            ctx: The command context
            text: The text to speak (optional)
        """
        if not text:
            await ctx.send("Usage: !tts <text to speak>")
            return

        try:
            if await self.bot._play_tts_response(text):
                await ctx.send(f"Playing TTS: {text}")
            else:
                await ctx.send("Failed to play TTS message. Please try again later.")
        except Exception as e:
            logger.error(f"Error in TTS command: {e}")
            await ctx.send("An error occurred while processing TTS command.") 