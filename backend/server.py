from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
import sqlite3
import json
import threading
import time
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
DB_FILE = "sensor_data.db"
BROKER = "localhost"
PORT = 1883

# Database Setup
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  type TEXT,
                  value REAL)''')
    conn.commit()
    conn.close()

init_db()

# MQTT Client
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code "+str(rc))
    client.subscribe("sensor/#")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Expected payload: {"timestamp": "...", "value": ..., "type": "..."}
        
        timestamp = payload.get('timestamp')
        sensor_type = payload.get('type')
        value = payload.get('value')

        if timestamp and sensor_type and value is not None:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO readings (timestamp, type, value) VALUES (?, ?, ?)",
                      (timestamp, sensor_type, value))
            conn.commit()
            conn.close()
            print(f"Saved: {sensor_type} - {value}")
    except Exception as e:
        print(f"Error processing message: {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Connection Error: {e}")

# Start MQTT in background thread
mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

# API Endpoints
@app.route('/api/history', methods=['GET'])
def get_history():
    sensor_type = request.args.get('type', 'temperature')
    limit = request.args.get('limit', 100)
    group_by = request.args.get('group_by', 'raw') # raw, hour, day
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if group_by == 'hour':
        # Group by YYYY-MM-DDTHH (first 13 chars)
        query = """
            SELECT substr(timestamp, 1, 13) as ts, AVG(value)
            FROM readings WHERE type=?
            GROUP BY ts
            ORDER BY ts DESC LIMIT ?
        """
        c.execute(query, (sensor_type, limit))
    elif group_by == 'day':
        # Group by YYYY-MM-DD (first 10 chars)
        query = """
            SELECT substr(timestamp, 1, 10) as ts, AVG(value)
            FROM readings WHERE type=?
            GROUP BY ts
            ORDER BY ts DESC LIMIT ?
        """
        c.execute(query, (sensor_type, limit))
    else:
        # Raw data
        c.execute("SELECT timestamp, value FROM readings WHERE type=? ORDER BY timestamp DESC LIMIT ?", (sensor_type, limit))
    
    data = c.fetchall()
    conn.close()
    
    # Return as list of dicts, reversed to show chronological order
    # For hour/day, we append :00:00 or T00:00:00 to make it look like a timestamp for frontend consistency if needed,
    # but frontend can handle partial strings too. Let's keep it simple.
    result = [{"timestamp": row[0], "value": row[1]} for row in reversed(data)]
    return jsonify(result)

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    sensor_type = request.args.get('type', 'temperature')
    group_by = request.args.get('group_by', 'raw')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get last 20 points (or groups) for prediction
    if group_by == 'hour':
        query = """
            SELECT AVG(value) FROM readings 
            WHERE type=? 
            GROUP BY substr(timestamp, 1, 13)
            ORDER BY substr(timestamp, 1, 13) DESC LIMIT 20
        """
        c.execute(query, (sensor_type,))
    elif group_by == 'day':
        query = """
            SELECT AVG(value) FROM readings 
            WHERE type=? 
            GROUP BY substr(timestamp, 1, 10)
            ORDER BY substr(timestamp, 1, 10) DESC LIMIT 20
        """
        c.execute(query, (sensor_type,))
    else:
        c.execute("SELECT value FROM readings WHERE type=? ORDER BY timestamp DESC LIMIT 20", (sensor_type,))
        
    data = c.fetchall()
    conn.close()
    
    if len(data) < 5:
        return jsonify({"error": "Not enough data for prediction"})
    
    values = [row[0] for row in reversed(data)]
    x = np.arange(len(values))
    y = np.array(values)
    
    # Simple Linear Regression (Polyfit degree 1)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    # Predict next 5 points
    next_x = np.arange(len(values), len(values) + 5)
    predicted_y = p(next_x)
    
    return jsonify({
        "current": values,
        "predicted": predicted_y.tolist(),
        "slope": z[0],
        "intercept": z[1]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
