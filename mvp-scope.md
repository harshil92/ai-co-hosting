## MVP Scope and Core Requirements

### 1. Twitch Chat Integration  
- **Core:**  
  - Connect to Twitch using tmi.js to listen for real-time chat messages.
  - Parse incoming messages and forward them to the dialogue engine.

### 2. Dialogue Generation via LLM  
- **Core:**  
  - Integrate an open source LLM (e.g., Llama 2 or GPT4All using vLLM) to generate responses based on incoming chat messages.
  - Maintain simple context (e.g., last few messages) for coherent replies.

### 3. Text-to-Speech (TTS)  
- **Core:**  
  - Convert the generated dialogue text to audio using Mozilla TTS or Coqui TTS.
  - Stream the synthesized audio into a file or output stream ready for OBS integration.

### 4. Avatar Rendering and Overlay  
- **Core:**  
  - Build a basic avatar overlay using Godot Engine.
  - Sync avatar animations (e.g., mouth movement) with the TTS audio output.

### 5. Basic Dashboard for Configuration  
- **Core:**  
  - A simple web dashboard (built with React or Next.js) to allow configuration of settings (e.g., toggling the virtual co-host on/off, setting personality parameters).

### 6. Integration with OBS  
- **Core:**  
  - Use OBS WebSocket (obs-websocket) to integrate the avatar overlay into the live stream.
