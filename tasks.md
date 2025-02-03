## MVP Trello Board Tasks

### **List: Setup and Planning**
- **Task 1:** Create project repository on GitHub and initialize Trello board.
- **Task 2:** Define MVP requirements and draft wireframes for the dashboard and overlay.
- **Task 3:** Choose open source tools: tmi.js for Twitch chat, Llama 2/GPT4All with vLLM for LLM, Mozilla/Coqui TTS for TTS, Godot for avatar, and OBS WebSocket for integration.

### **List: Twitch Chat Integration**
- **Task 4:** Set up a basic Node.js or Python (FastAPI) service to connect to Twitch chat using tmi.js.
- **Task 5:** Implement message listener that logs incoming messages.
- **Task 6:** Create a simple parser to filter and format chat messages for the dialogue engine.

### **List: Dialogue Generation (LLM Integration)**
- **Task 7:** Set up LLM inference using an open source model (Llama 2/GPT4All) with vLLM.
- **Task 8:** Create a simple API endpoint that takes chat input and returns generated dialogue.
- **Task 9:** Integrate context management (e.g., store last 5 messages) to feed into the LLM.

### **List: Text-to-Speech Integration**
- **Task 10:** Install and configure Mozilla TTS/Coqui TTS on the development server.
- **Task 11:** Create a module to convert generated text to audio files or streams.
- **Task 12:** Test audio output and ensure synchronization with text.

### **List: Avatar Rendering and Overlay**
- **Task 13:** Set up a basic Godot project to render a 2D avatar.
- **Task 14:** Integrate simple animations (idle, speaking/mouth movement) that can be triggered.
- **Task 15:** Develop a simple API or interface in Godot that accepts triggers (e.g., when audio starts) to animate the avatar.

### **List: Dashboard Development**
- **Task 16:** Set up a basic React/Next.js project for the dashboard.
- **Task 17:** Create UI components to display status (online/offline, chat logs, current response).
- **Task 18:** Implement settings controls (toggle co-host, adjust personality parameters, etc.).

### **List: OBS Integration**
- **Task 19:** Research and set up OBS WebSocket in your local OBS installation.
- **Task 20:** Create a simple script that connects to OBS via obs-websocket and triggers the overlay (e.g., displaying the avatar).
- **Task 21:** Test end-to-end integration by streaming a test session with the overlay.

### **List: Testing, Optimization, and Deployment**
- **Task 22:** Conduct unit tests for each module (Twitch chat, LLM response, TTS, avatar animation, dashboard API).
- **Task 23:** Perform integration testing of all components.
- **Task 24:** Optimize performance for low latency (profile LLM inference, TTS conversion, and WebSocket communication).
- **Task 25:** Containerize the MVP using Docker.
- **Task 26:** Set up a CI/CD pipeline with GitHub Actions.
- **Task 27:** Deploy the MVP to a staging environment (e.g., on AWS/GCP/Azure) for beta testing.
