"""Main entry point for the AI Co-host Twitch Bot."""
import uvicorn
import logging
from twitch_bot.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the application."""
    try:
        logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
        uvicorn.run(
            "twitch_bot.bot:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_DEBUG,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main() 