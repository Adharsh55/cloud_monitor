import logging
import threading
import time
import psutil
from flask import Flask, jsonify, render_template, Response
from prometheus_client import generate_latest, Gauge, Counter
from utils.metrics import get_system_metrics

# ---------------------------------------------------------
# 1. PROMETHEUS SETUP
# ---------------------------------------------------------
PROM_CPU = Gauge('system_cpu_usage', 'Current CPU usage percentage')
PROM_MEM = Gauge('system_memory_usage', 'Current RAM usage percentage')
PROM_LOGS = Counter('system_logs_generated', 'Total number of logs generated', ['level'])

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logs_store = []

# ---------------------------------------------------------
# 2. MONITORING THREAD
# ---------------------------------------------------------
def add_log(level, message):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"{timestamp} | {level.upper()} | {message}"
    logs_store.append(entry)
    if len(logs_store) > 100:
        logs_store.pop(0)
    PROM_LOGS.labels(level=level).inc()

def background_monitor():
    print(" -> Live Monitor & Prometheus Exporter Started...")
    while True:
        try:
            time.sleep(2)
            metrics = get_system_metrics()
            cpu = metrics['cpu']
            mem = metrics['memory']['percent']

            # Update Prometheus
            PROM_CPU.set(cpu)
            PROM_MEM.set(mem)

            # Generate Logs
            if cpu > 50:
                 add_log("warning", f"High CPU Load: {cpu}%")
            elif mem > 80:
                 add_log("warning", f"Memory Critical: {mem}%")
            else:
                 add_log("info", f"System Stable: CPU {cpu}% - RAM {mem}%")

        except Exception as e:
            print(f"Error: {e}")

t = threading.Thread(target=background_monitor, daemon=True)
t.start()

# ---------------------------------------------------------
# 3. DIRECT ROUTES (No Login/Permission)
# ---------------------------------------------------------
@app.route("/")
def index():
    # GO STRAIGHT TO DASHBOARD
    return render_template("dashboard.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Prometheus Scraper URL
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

# Frontend Data API
@app.route("/api/data")
def api_data():
    return jsonify({
        "metrics": get_system_metrics(),
        "logs": logs_store
    })

if __name__ == "__main__":
    print("SYSTEM ONLINE: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)