from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from .dialogue_manager import DialogueManager

app = FastAPI(title="AI Co-Host LLM Service")
dialogue_manager = DialogueManager()

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

@app.get("/health")
async def health_check():
    """Check if the LLM service is available."""
    is_available = dialogue_manager.llm_client.is_available()
    return {
        "status": "healthy" if is_available else "unhealthy",
        "llm_available": is_available,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def generate_chat_response(chat_message: ChatMessage):
    """Generate a response to a chat message."""
    try:
        # Add the message to context
        dialogue_manager.add_message(
            username=chat_message.username,
            message=chat_message.message,
            emotes=chat_message.emotes
        )
        
        # Generate response
        response = dialogue_manager.generate_response()
        
        if not response:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response"
            )
            
        # Get current context info
        context_info = dialogue_manager.get_context_info()
            
        return ChatResponse(
            response=response,
            context_summary=context_info["metadata"]["context_summary"],
            current_topics=list(context_info["metadata"]["current_topics"])
        )
        
    except Exception as e:
        return ChatResponse(
            response="I'm having trouble processing that message right now!",
            error=str(e)
        )

@app.get("/context", response_model=ContextInfo)
async def get_context():
    """Get detailed information about the current conversation context."""
    return dialogue_manager.get_context_info()

@app.delete("/context")
async def clear_context():
    """Clear the current conversation context."""
    dialogue_manager.__init__()  # Reinitialize the dialogue manager
    return {"status": "success", "message": "Context cleared"} 