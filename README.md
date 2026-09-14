# Smart Home Device Monitoring System

A full-stack smart home monitoring application that simulates security device events and displays device status updates in real time.

🔗 **Live Demo:** https://smart-home-monitor.pages.dev

## Overview

This project simulates a cloud-connected home security system with three devices:

- Door Sensor
- Motion Sensor
- Security Camera

Users can simulate an intrusion directly from the dashboard. The backend processes the device events, stores them in SQLite, and sends real-time updates to connected clients through WebSockets.

For example, an intrusion simulation generates:

- Front Door → `OPEN`
- Motion Sensor → `MOTION_DETECTED`
- Camera → `RECORDING`

The system can also be reset to:

- Front Door → `CLOSED`
- Motion Sensor → `CLEAR`
- Camera → `IDLE`

## Architecture

```text
                    REST API
React Dashboard ───────────────► FastAPI Backend
       ▲                              │
       │                              │
       │ WebSocket                    ▼
       └──────────────────────── SQLite Database
                                      │
                                      ▼
                               Device Event History
```

### Event Flow

```text
Simulate Intrusion
        │
        ▼
POST /simulate/intrusion
        │
        ▼
FastAPI Backend
        │
        ├── Door Sensor → OPEN
        ├── Motion Sensor → MOTION_DETECTED
        └── Camera → RECORDING
        │
        ▼
SQLite
        │
        ▼
WebSocket Broadcast
        │
        ▼
React Dashboard
```

## Features

- Real-time device status monitoring
- REST API for device events
- WebSocket-based live updates
- Persistent event history with SQLite
- Intrusion simulation
- System reset simulation
- Responsive web dashboard
- Public live demo

## Tech Stack

**Frontend**
- React
- JavaScript
- Vite
- CSS

**Backend**
- Python
- FastAPI
- WebSockets
- SQLite

**Deployment**
- Cloudflare Pages

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API health/root endpoint |
| `GET` | `/events` | Retrieve device event history |
| `POST` | `/events` | Create a device event |
| `POST` | `/simulate/intrusion` | Simulate an intrusion |
| `POST` | `/simulate/reset` | Reset devices to normal state |

## Example Device Event

```json
{
  "device_id": "door-001",
  "device_type": "door_sensor",
  "status": "OPEN"
}
```

## Real-Time Updates

When the backend receives or generates a device event, it persists the event and broadcasts the update to connected dashboard clients through WebSockets.

This allows device states and recent events to update without requiring the user to refresh the page.

## Running Locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open the local URL provided by Vite.

## What I Learned

Through this project, I practiced building a full-stack event-driven application involving REST APIs, persistent storage, real-time WebSocket communication, and frontend state synchronization.

I also gained experience designing interactions between simulated IoT devices, backend services, and a monitoring dashboard.