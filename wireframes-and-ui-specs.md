## Dashboard and Overlay Wireframe Specifications

### 1. Streamer Dashboard

#### Layout Structure
```
+----------------------------------+
|           Header Bar             |
+------------+---------------------+
|            |                     |
| Navigation | Main Content Area   |
|   Panel    |                     |
|            |                     |
|            |                     |
+------------+---------------------+
```

#### Components

1. **Header Bar**
   - System status indicator (Online/Offline)
   - Current stream duration
   - Quick actions (Start/Stop Co-host, Emergency Mute)

2. **Navigation Panel**
   - Dashboard (Home)
   - Settings
   - Analytics
   - Logs

3. **Main Content Area**
   - **Dashboard View**
     ```
     +----------------------------------+
     | Co-host Status                   |
     +----------------------------------+
     | Recent Chat History              |
     +----------------------------------+
     | Current Response                 |
     +----------------------------------+
     | Performance Metrics              |
     +----------------------------------+
     ```
   
   - **Settings View**
     ```
     +----------------------------------+
     | Co-host Personality Settings     |
     +----------------------------------+
     | Voice Settings                   |
     +----------------------------------+
     | Avatar Settings                  |
     +----------------------------------+
     | Integration Settings             |
     +----------------------------------+
     ```

### 2. Stream Overlay

#### Layout Structure
```
+----------------------------------+
|                                  |
|              Stream              |
|                                  |
|                                  |
|     +-----------------+          |
|     |  Avatar Window  |          |
|     +-----------------+          |
|                                  |
+----------------------------------+
```

#### Components

1. **Avatar Window**
   - Transparent background
   - Configurable position (draggable in OBS)
   - Default size: 320x320 pixels
   - Scalable without quality loss

2. **Avatar States**
   - Idle animation
   - Speaking animation
   - Reaction animations (happy, thinking, surprised)
   - Smooth transitions between states

3. **Optional Elements**
   - Speech bubble/caption area
   - Mood indicator
   - Interactive elements (viewer polls, reactions)

### Technical Specifications

1. **Dashboard Technical Requirements**
   - Responsive design (minimum width: 1024px)
   - Dark/Light theme support
   - Real-time updates using WebSocket
   - Local storage for user preferences
   - Cross-browser compatibility

2. **Overlay Technical Requirements**
   - WebGL rendering for avatar
   - Transparent background support
   - Hardware acceleration
   - Low resource usage
   - OBS browser source compatible

3. **Performance Targets**
   - Dashboard initial load: < 2s
   - Real-time updates: < 100ms latency
   - Avatar animation FPS: 60
   - Memory usage: < 200MB 