import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    setConnectionStatus("connecting");

    const socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      console.log("WebSocket connected");
      setConnectionStatus("connected");
    };

    socket.onmessage = (event) => {
      const newEvent = JSON.parse(event.data);

      setEvents((prevEvents) => [newEvent, ...prevEvents]);
    };

    socket.onerror = () => {
      console.error("WebSocket error");
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
      setConnectionStatus("disconnected");
    };

    return () => {
      socket.close();
    };
  }, []);

  const getLatestStatus = (deviceType) => {
    const latestEvent = events.find(
      (event) => event.device_type === deviceType
    );

    return latestEvent ? latestEvent.status : "UNKNOWN";
  };

  const getStatusClass = (status) => {
    if (status === "CLOSED" || status === "CLEAR" || status === "IDLE") {
      return "status-safe";
    }

    if (
      status === "OPEN" ||
      status === "MOTION_DETECTED" ||
      status === "RECORDING"
    ) {
      return "status-active";
    }

    return "";
  };

  const simulateIntrusion = () => {
    fetch(`${import.meta.env.VITE_API_URL}/simulate/intrusion`, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Intrusion simulated:", data);
      })
      .catch((error) => {
        console.error("Failed to simulate intrusion:", error);
      });
  };

  const resetSystem = () => {
    fetch(`${import.meta.env.VITE_API_URL}/simulate/reset`, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("System reset:", data);
      })
      .catch((error) => {
        console.error("Failed to reset system:", error);
      });
  };

  const doorStatus = getLatestStatus("door_sensor");
  const motionStatus = getLatestStatus("motion_sensor");
  const cameraStatus = getLatestStatus("camera");

  return (
    <div className="dashboard">
      <h1>Smart Home Monitor</h1>
      
      <div className="connection-status">
        <span
          className={`connection-dot ${connectionStatus}`}
        ></span>

        {connectionStatus === "connected"
          ? "Live"
          : connectionStatus === "connecting"
          ? "Connecting to server..."
          : "Disconnected"}
      </div>
      <p className="subtitle">Device Cloud Monitoring Dashboard</p>
      
      <div className="controls">
        <button onClick={simulateIntrusion}>
          Simulate Intrusion
        </button>

        <button onClick={resetSystem}>
          Reset System
        </button>
      </div>


      <section>
        <h2>Devices</h2>

        <div className="device-grid">
          <div className="device-card">
            <h3>Front Door</h3>
            <p>Door Sensor</p>
            <h3 className={getStatusClass(doorStatus)}>
              {doorStatus}
            </h3>
          </div>

          <div className="device-card">
            <h3>Motion Sensor</h3>
            <p>Motion Detection</p>
            <h3 className={getStatusClass(motionStatus)}>
              {motionStatus}
            </h3>
          </div>

          <div className="device-card">
            <h3>Camera</h3>
            <p>Security Camera</p>
            <h3 className={getStatusClass(cameraStatus)}>
              {cameraStatus}
            </h3>
          </div>
        </div>
      </section>

      <section className="events-section">
        <h2>Recent Events</h2>

        <div className="event-list">
          {events.map((event) => (
            <div className="event-card" key={event.id}>
              <div>
                <h3>{event.device_id}</h3>
                <p>{event.device_type}</p>
              </div>

              <div className="event-info">
                <strong>{event.status}</strong>
                <span>{event.created_at}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;