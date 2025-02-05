import requests
import json
from time import sleep

def test_api(base_url: str = "http://localhost:8001"):
    """Test the LLM service API endpoints.
    
    Args:
        base_url: Base URL of the API server.
    """
    # Test health check
    print("\nTesting health check endpoint...")
    health_response = requests.get(f"{base_url}/health")
    print(f"Health status: {health_response.json()}")
    
    if health_response.json().get("llm_available", False):
        # Test chat endpoint
        print("\nTesting chat endpoint...")
        chat_data = {
            "username": "test_user",
            "message": "Hey there!"
        }
        
        chat_response = requests.post(
            f"{base_url}/chat",
            json=chat_data
        )
        print(f"Chat response: {chat_response.json()}")
        
        # Test context endpoint
        print("\nTesting context endpoint...")
        context_response = requests.get(f"{base_url}/context")
        print(f"Current context: {json.dumps(context_response.json(), indent=2)}")
    else:
        print("\nWarning: LLM is not available. Make sure LM Studio is running!")

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure both the API server and LM Studio are running!")
    sleep(2)  # Give user time to read the message
    test_api() 