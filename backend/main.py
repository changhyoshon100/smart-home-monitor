from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()
active_connections = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DeviceEvent(BaseModel):
    device_id: str
    device_type: str
    status: str


def init_db():
    conn = sqlite3.connect("events.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            device_type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.get("/")
def root():
    return {
        "message": "Smart Home Device Monitoring API"
    }


@app.post("/events")
async def create_event(event: DeviceEvent):
    conn = sqlite3.connect("events.db")

    cursor = conn.execute(
        """
        INSERT INTO events (device_id, device_type, status)
        VALUES (?, ?, ?)
        """,
        (
            event.device_id,
            event.device_type,
            event.status
        )
    )

    conn.commit()
    event_id = cursor.lastrowid

    # 방금 저장된 이벤트를 다시 읽어서 created_at까지 가져오기
    row = conn.execute(
        """
        SELECT id, device_id, device_type, status, created_at
        FROM events
        WHERE id = ?
        """,
        (event_id,)
    ).fetchone()

    new_event = {
        "id": row[0],
        "device_id": row[1],
        "device_type": row[2],
        "status": row[3],
        "created_at": row[4]
    }

    # React에게 즉시 push
    await broadcast_event(new_event)

    camera_event_id = None

    if (
        event.device_type == "motion_sensor"
        and event.status == "MOTION_DETECTED"
    ):
        camera_cursor = conn.execute(
            """
            INSERT INTO events (device_id, device_type, status)
            VALUES (?, ?, ?)
            """,
            (
                "camera-001",
                "camera",
                "RECORDING"
            )
        )

        conn.commit()
        camera_event_id = camera_cursor.lastrowid

        camera_row = conn.execute(
            """
            SELECT id, device_id, device_type, status, created_at
            FROM events
            WHERE id = ?
            """,
            (camera_event_id,)
        ).fetchone()

        camera_event = {
            "id": camera_row[0],
            "device_id": camera_row[1],
            "device_type": camera_row[2],
            "status": camera_row[3],
            "created_at": camera_row[4]
        }

        await broadcast_event(camera_event)

    conn.close()

    return {
        "message": "Event stored",
        "event_id": event_id,
        "camera_event_id": camera_event_id,
        "event": new_event
    }

@app.post("/simulate/intrusion")
async def simulate_intrusion():
    events = [
        {
            "device_id": "door-001",
            "device_type": "door_sensor",
            "status": "OPEN",
        },
        {
            "device_id": "motion-001",
            "device_type": "motion_sensor",
            "status": "MOTION_DETECTED",
        },
        {
            "device_id": "camera-001",
            "device_type": "camera",
            "status": "RECORDING",
        },
    ]

    conn = sqlite3.connect("events.db")

    created_events = []

    for event in events:
        cursor = conn.execute(
            """
            INSERT INTO events (device_id, device_type, status)
            VALUES (?, ?, ?)
            """,
            (
                event["device_id"],
                event["device_type"],
                event["status"],
            ),
        )

        created_event = {
            "id": cursor.lastrowid,
            "device_id": event["device_id"],
            "device_type": event["device_type"],
            "status": event["status"],
        }

        created_events.append(created_event)

    conn.commit()
    conn.close()

    for event in created_events:
        await broadcast_event(event)

    return {
        "message": "Intrusion simulated",
        "events": created_events,
    }


@app.post("/simulate/reset")
async def reset_system():
    events = [
        {
            "device_id": "door-001",
            "device_type": "door_sensor",
            "status": "CLOSED",
        },
        {
            "device_id": "motion-001",
            "device_type": "motion_sensor",
            "status": "CLEAR",
        },
        {
            "device_id": "camera-001",
            "device_type": "camera",
            "status": "IDLE",
        },
    ]

    conn = sqlite3.connect("events.db")

    created_events = []

    for event in events:
        cursor = conn.execute(
            """
            INSERT INTO events (device_id, device_type, status)
            VALUES (?, ?, ?)
            """,
            (
                event["device_id"],
                event["device_type"],
                event["status"],
            ),
        )

        created_event = {
            "id": cursor.lastrowid,
            "device_id": event["device_id"],
            "device_type": event["device_type"],
            "status": event["status"],
        }

        created_events.append(created_event)

    conn.commit()
    conn.close()

    for event in created_events:
        await broadcast_event(event)

    return {
        "message": "System reset",
        "events": created_events,
    }



@app.get("/events")
def get_events():
    conn = sqlite3.connect("events.db")

    cursor = conn.execute("""
        SELECT id, device_id, device_type, status, created_at
        FROM events
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "device_id": row[1],
            "device_type": row[2],
            "status": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    active_connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_event(event_data):
    disconnected = []

    for connection in active_connections:
        try:
            await connection.send_json(event_data)
        except:
            disconnected.append(connection)

    for connection in disconnected:
        active_connections.remove(connection)