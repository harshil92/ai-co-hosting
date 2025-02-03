"""Main entry point for the AI Co-host Twitch Bot."""
import uvicorn
from twitch_bot.config import settings

def main():
    """Run the application."""
    uvicorn.run(
        "twitch_bot.bot:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

if __name__ == "__main__":
    main() 