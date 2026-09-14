# Smart Home Device Monitoring System

A full-stack smart home monitoring application that simulates cloud communication between home security devices and a monitoring dashboard.

The system processes device events through a FastAPI backend, stores event history in SQLite, and delivers real-time updates to a React dashboard using WebSockets.

## Features

- Monitor door, motion sensor, and camera states
- Process device events through REST APIs
- Persist device events in SQLite
- Automatically trigger camera recording when motion is detected
- Display current device states and recent event history
- Push new events to the dashboard in real time using WebSockets
- Display WebSocket connection status

## Architecture

Device / Sensor Simulation
        |
        | POST /events
        v
FastAPI Backend
        |
        +----> SQLite Database
        |
        +----> Automation Rules
        |        |
        |        +--> Motion Detected → Camera Recording
        |
        +----> WebSocket
                 |
                 v
          React Dashboard

## Tech Stack

### Backend
- Python
- FastAPI
- SQLite
- REST API
- WebSocket

### Frontend
- React
- JavaScript
- Vite
- CSS

## Example Event

```json
{
  "device_id": "motion-001",
  "device_type": "motion_sensor",
  "status": "MOTION_DETECTED"
}

When a motion event is received, the backend stores the event and triggers a camera recording event. Connected dashboard clients receive the new events through WebSocket communication.

Running Locally
Backend
    cd backend
    source venv/bin/activate
    uvicorn main:app --reload

The backend runs on:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Frontend
    cd frontend
    npm install
    npm run dev