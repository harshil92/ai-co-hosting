## 3. System Architecture

### Core Components

1. **Frontend Interface:**
   - **Streamer Dashboard:**  
     Built with open source frameworks such as React or Next.js.
   - **Avatar Overlay Module:**  
     A Godot-based or OBS WebSocket-integrated module that renders the animated avatar over the live stream.

2. **Backend Services:**
   - **Chat Listener & Processor:**  
     A Node.js or Python (FastAPI) service using tmi.js and Twitch API for real-time message ingestion.
   - **LLM Dialogue Engine:**  
     Powered by Llama 2 or GPT4All using vLLM for fast inference; integrated with a context manager using FAISS.
   - **TTS Service:**  
     Using Mozilla TTS or Coqui TTS to convert text into audio streams.
   - **Moderation Engine:**  
     Custom-built filters and NLP-based moderation using Hugging Face models.
   - **Analytics & Logging Service:**  
     Utilizing PostgreSQL (or MongoDB) for data storage, along with Prometheus/Grafana for monitoring.

3. **Integration Layer:**
   - **Twitch API Connector:**  
     Connecting via official Twitch APIs and tmi.js.
   - **OBS Integration:**  
     Use obs-websocket to relay events from the backend to the live stream software.

4. **Deployment & Infrastructure:**
   - **Containerization:**  
     Use Docker and orchestrate with Kubernetes.
   - **CI/CD:**  
     Set up pipelines using GitHub Actions (open source friendly).
