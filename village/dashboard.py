# dashboard.py
# A simple Flask web dashboard that receives MQTT data
# from multiple hydroelectric stations and displays it live.

import time
import json
import threading
from flask import Flask, render_template_string
import paho.mqtt.client as mqtt

# ---------- SETTINGS ----------
MQTT_BROKER = "hydrobroker"     # same broker the Pis publish to
MQTT_PORT = 1883
MQTT_TOPIC = "hydro/#"          # subscribe to ALL stations (hydro/0, hydro/1, etc.)
NUM_STATIONS = 10               # how many stations you expect
# --------------------------------

# This dictionary stores the latest data from each station.
# Key   = station number (string like "0", "1", "2")
# Value = dictionary with energy reading and timestamp
stations = {}

# ---------- MQTT SETUP ----------
# This section connects to the MQTT broker and listens
# for messages from all the hydroelectric stations.

def on_connect(client, userdata, flags, rc):
    """Called when we successfully connect to the MQTT broker."""
    print(f"Connected to MQTT broker (code {rc})")
    # Subscribe to all hydro topics: hydro/0, hydro/1, hydro/2, etc.
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    """Called every time a message arrives from any station."""
    try:
        # msg.topic looks like "hydro/3"
        # We split on "/" and take the last part to get the station number
        station_id = msg.topic.split("/")[-1]

        # The payload is the energy percentage (0-100) sent by the Pi
        energy = int(msg.payload.decode("utf-8"))

        # Store it with a timestamp
        stations[station_id] = {
            "energy": energy,
            "last_update": time.time()
        }

        print(f"Station {station_id}: energy = {energy}%")

    except Exception as e:
        print(f"Error processing message: {e}")

def start_mqtt():
    """Start the MQTT client in a background thread."""
    client = mqtt.Client(client_id="dashboard")
    client.on_connect = on_connect
    client.on_message = on_message

    # Keep trying to connect (broker might not be ready yet)
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            break
        except Exception as e:
            print(f"Waiting for MQTT broker... ({e})")
            time.sleep(2)

    # loop_forever() blocks, so we run it in a thread
    client.loop_forever()

# ---------- FLASK WEB APP ----------
app = Flask(__name__)

# The HTML template for the dashboard
# It auto-refreshes every 2 seconds so you see live updates
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hydroelectric Dashboard</title>
    <meta http-equiv="refresh" content="2">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            color: white;
            padding: 20px;
        }

        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }

        /* Summary bar at the top */
        .summary {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 30px;
        }

        .summary-box {
            background: #16213e;
            border-radius: 10px;
            padding: 20px 40px;
            text-align: center;
        }

        .summary-box .label {
            font-size: 14px;
            color: #888;
        }

        .summary-box .value {
            font-size: 36px;
            font-weight: bold;
            color: #00d4ff;
        }

        /* Grid of station cards */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            max-width: 1000px;
            margin: 0 auto;
        }

        .card {
            background: #16213e;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }

        .card h3 {
            margin-bottom: 10px;
            font-size: 16px;
            color: #ccc;
        }

        .card .reading {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* The bar that fills up based on energy % */
        .bar-container {
            background: #0a0a1a;
            border-radius: 5px;
            height: 20px;
            overflow: hidden;
        }

        .bar-fill {
            height: 100%;
            border-radius: 5px;
            transition: width 0.5s;
        }

        .card .status {
            margin-top: 8px;
            font-size: 12px;
            color: #888;
        }

        /* Colour the reading based on energy level */
        .level-high   { color: #00ff88; }
        .level-medium { color: #ffcc00; }
        .level-low    { color: #ff4444; }
        .level-off    { color: #555;    }

        .bar-high   { background: #00ff88; }
        .bar-medium { background: #ffcc00; }
        .bar-low    { background: #ff4444; }
        .bar-off    { background: #555;    }

        .offline {
            opacity: 0.4;
        }
    </style>
</head>
<body>
    <h1>⚡ Hydroelectric Dashboard</h1>
    <p class="subtitle">Live generation from {{ total_stations }} stations</p>

    <!-- Summary section -->
    <div class="summary">
        <div class="summary-box">
            <div class="label">Stations Online</div>
            <div class="value">{{ online_count }}</div>
        </div>
        <div class="summary-box">
            <div class="label">Total Generation</div>
            <div class="value">{{ total_energy }}%</div>
        </div>
        <div class="summary-box">
            <div class="label">Average Generation</div>
            <div class="value">{{ avg_energy }}%</div>
        </div>
        <div class="summary-box">
            <div class="label">Best Station</div>
            <div class="value">{{ best_station }}</div>
        </div>
    </div>

    <!-- Station cards -->
    <div class="grid">
        {% for station in station_list %}
        <div class="card {{ 'offline' if not station.online }}">
            <h3>Station {{ station.id }}</h3>

            {% if station.online %}
                <div class="reading {{ station.level_class }}">
                    {{ station.energy }}%
                </div>
                <div class="bar-container">
                    <div class="bar-fill {{ station.bar_class }}"
                         style="width: {{ station.energy }}%;">
                    </div>
                </div>
                <div class="status">
                    Updated {{ station.age }}s ago
                </div>
            {% else %}
                <div class="reading level-off">offline</div>
                <div class="bar-container">
                    <div class="bar-fill bar-off" style="width: 0%;"></div>
                </div>
                <div class="status">No data received</div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def dashboard():
    """Build the dashboard page from the latest station data."""
    now = time.time()
    station_list = []
    online_count = 0
    total_energy = 0
    best_energy = -1
    best_id = "-"

    # Build a list of all stations (0 to NUM_STATIONS-1)
    for i in range(NUM_STATIONS):
        sid = str(i)

        if sid in stations:
            data = stations[sid]
            age = int(now - data["last_update"])
            online = age < 10  # consider "offline" if no update in 10 seconds
            energy = data["energy"]

            # Pick a colour level based on energy %
            if energy >= 60:
                level_class = "level-high"
                bar_class = "bar-high"
            elif energy >= 30:
                level_class = "level-medium"
                bar_class = "bar-medium"
            else:
                level_class = "level-low"
                bar_class = "bar-low"

            if online:
                online_count += 1
                total_energy += energy
                if energy > best_energy:
                    best_energy = energy
                    best_id = f"#{sid}"

            station_list.append({
                "id": sid,
                "energy": energy,
                "online": online,
                "age": age,
                "level_class": level_class,
                "bar_class": bar_class
            })
        else:
            # Never heard from this station
            station_list.append({
                "id": sid,
                "energy": 0,
                "online": False,
                "age": 0,
                "level_class": "level-off",
                "bar_class": "bar-off"
            })

    # Compute averages
    avg_energy = round(total_energy / online_count) if online_count > 0 else 0

    return render_template_string(
        DASHBOARD_HTML,
        station_list=station_list,
        total_stations=NUM_STATIONS,
        online_count=online_count,
        total_energy=total_energy,
        avg_energy=avg_energy,
        best_station=best_id
    )

# ---------- START EVERYTHING ----------
if __name__ == "__main__":
    # Start MQTT listener in background thread
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()

    print("Starting dashboard at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)