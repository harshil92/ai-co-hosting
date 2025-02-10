from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
from contextlib import asynccontextmanager
from .dialogue_manager import DialogueManager
from .llm_client import LMStudioClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
llm_client: Optional[LMStudioClient] = None
dialogue_manager: Optional[DialogueManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    global llm_client, dialogue_manager
    
    # Initialize services
    logger.info("Initializing LLM service...")
    llm_client = LMStudioClient()
    dialogue_manager = DialogueManager(llm_client)
    
    yield
    
    # Cleanup
    logger.info("Shutting down LLM service...")
    if llm_client:
        await llm_client.__aexit__(None, None, None)

app = FastAPI(
    title="AI Co-Host LLM Service",
    lifespan=lifespan
)

class ChatMessage(BaseModel):
    username: str
    message: str
    emotes: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()
    context_summary: Optional[str] = None
    current_topics: Optional[List[str]] = None

class ContextInfo(BaseModel):
    context: List[Dict]
    metadata: Dict
    system_prompt: str

async def get_dialogue_manager() -> DialogueManager:
    """Dependency to get the current dialogue manager instance."""
    if not dialogue_manager:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized"
        )
    return dialogue_manager

@app.get("/health")
async def health_check(dm: DialogueManager = Depends(get_dialogue_manager)):
    """Check if the LLM service is available."""
    is_available = await dm.llm_client.is_available()
    return {
        "status": "healthy" if is_available else "unhealthy",
        "llm_available": is_available,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def generate_chat_response(
    chat_message: ChatMessage,
    dm: DialogueManager = Depends(get_dialogue_manager)
):
    """Generate a response to a chat message."""
    try:
        # Add the message to context
        dm.add_message(
            username=chat_message.username,
            message=chat_message.message,
            emotes=chat_message.emotes
        )
        
        # Generate response
        response = await dm.generate_response()
        
        if not response:
            logger.error("Failed to generate response")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response"
            )
            
        # Get current context info
        context_info = dm.get_context_info()
            
        return ChatResponse(
            response=response,
            context_summary=context_info["metadata"]["context_summary"],
            current_topics=list(context_info["metadata"]["current_topics"])
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/context", response_model=ContextInfo)
async def get_context(dm: DialogueManager = Depends(get_dialogue_manager)):
    """Get detailed information about the current conversation context."""
    try:
        return dm.get_context_info()
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.delete("/context")
async def clear_context(dm: DialogueManager = Depends(get_dialogue_manager)):
    """Clear the current conversation context."""
    try:
        global dialogue_manager
        dialogue_manager = DialogueManager(llm_client)
        return {
            "status": "success",
            "message": "Context cleared",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 