import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import time
import threading
import os
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuration
BROKER = "localhost"
PORT = 1883
DATA_DIR = "../data"
STATE_FILE = "publisher_state.json"

class PublisherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Data Publisher")
        self.root.geometry("600x500")

        self.is_running = False
        self.client = mqtt.Client()
        self.data_queue = []
        self.current_index = 0

        # UI Elements
        self.setup_ui()
        
        # Load Data
        self.load_data()
        
        # Load State
        self.load_state()

    def setup_ui(self):
        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        self.btn_start = ttk.Button(control_frame, text="Start Publishing", command=self.start_publishing)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(control_frame, text="Stop", command=self.stop_publishing, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_reset = ttk.Button(control_frame, text="Reset Progress", command=self.reset_progress)
        self.btn_reset.pack(side="left", padx=5)

        ttk.Label(control_frame, text="Interval (ms):").pack(side="left", padx=5)
        self.interval_var = tk.IntVar(value=1000)
        self.spin_interval = ttk.Spinbox(control_frame, from_=100, to=5000, textvariable=self.interval_var, width=5)
        self.spin_interval.pack(side="left", padx=5)

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Status", padding=10)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(status_frame, height=15)
        self.log_area.pack(fill="both", expand=True)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", padx=10, pady=5)

    def log(self, message):
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)

    def load_data(self):
        self.log("Loading data files...")
        self.data_points = []
        
        files = {
            "temperature": "temperature.txt",
            "humidity": "humidity.txt",
            "pressure": "pressure.txt"
        }

        for sensor_type, filename in files.items():
            path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(path):
                self.log(f"Error: File {path} not found.")
                continue
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            # Parse the line which is a JSON object {"time": "val", ...}
                            chunk = json.loads(line)
                            for ts, val in chunk.items():
                                if val is None or val == "":
                                    continue
                                try:
                                    float_val = float(val)
                                    self.data_points.append({
                                        "timestamp": ts,
                                        "value": float_val,
                                        "type": sensor_type
                                    })
                                except ValueError:
                                    continue
                        except json.JSONDecodeError:
                            self.log(f"Skipping invalid JSON line in {filename}")
            except Exception as e:
                self.log(f"Error reading {filename}: {e}")

        # Sort by timestamp
        self.data_points.sort(key=lambda x: x['timestamp'])
        self.log(f"Loaded {len(self.data_points)} data points.")
        self.progress['maximum'] = len(self.data_points)

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    self.current_index = state.get('current_index', 0)
                    self.log(f"Restored progress: {self.current_index}/{len(self.data_points)}")
            except:
                self.log("Failed to load state.")

    def save_state(self):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({'current_index': self.current_index}, f)
        except Exception as e:
            print(f"Failed to save state: {e}")

    def reset_progress(self):
        self.current_index = 0
        self.save_state()
        self.log("Progress reset to 0.")
        self.progress_var.set(0)

    def start_publishing(self):
        if not self.data_points:
            self.log("No data to publish.")
            return

        try:
            self.client.connect(BROKER, PORT, 60)
            self.client.loop_start()
            self.log(f"Connected to MQTT Broker at {BROKER}:{PORT}")
        except Exception as e:
            self.log(f"Connection failed: {e}")
            return

        self.is_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_reset.config(state="disabled")
        
        # Start thread
        threading.Thread(target=self.publish_loop, daemon=True).start()

    def stop_publishing(self):
        self.is_running = False
        self.client.loop_stop()
        self.client.disconnect()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_reset.config(state="normal")
        self.save_state()
        self.log("Stopped publishing.")

    def publish_loop(self):
        while self.is_running and self.current_index < len(self.data_points):
            point = self.data_points[self.current_index]
            
            # Construct payload strictly as per requirement image if needed, 
            # but for better backend handling, let's use a standard clear format.
            # Requirement says: {"year-month-dateThour:minute:second": "temperature", ...}
            # But that's the FILE format. The MQTT payload usually should be self-contained.
            # I will send: {"timestamp": "...", "value": ..., "type": "..."}
            
            payload = json.dumps(point)
            topic = f"sensor/{point['type']}"
            
            self.client.publish(topic, payload)
            
            # Update UI in main thread
            self.root.after(0, self.update_ui, point, self.current_index)
            
            self.current_index += 1
            
            # Save state periodically (every 10 points)
            if self.current_index % 10 == 0:
                self.save_state()
                
            time.sleep(self.interval_var.get() / 1000.0)
        
        if self.current_index >= len(self.data_points):
            self.root.after(0, self.stop_publishing)
            self.root.after(0, lambda: self.log("Finished publishing all data."))

    def update_ui(self, point, index):
        self.log(f"Published to {point['type']}: {point['value']} at {point['timestamp']}")
        self.progress_var.set(index)

if __name__ == "__main__":
    root = tk.Tk()
    app = PublisherApp(root)
    root.mainloop()
