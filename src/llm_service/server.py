import uvicorn
from .api import app

def run_server(host: str = "0.0.0.0", port: int = 8001):
    """Run the LLM service server.
    
    Args:
        host: Host to bind the server to.
        port: Port to run the server on.
    """
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    run_server() 