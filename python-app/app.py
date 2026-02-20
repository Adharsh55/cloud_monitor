from flask import Flask, render_template, Response
import psutil
import threading
import time
import numpy as np
from sklearn.ensemble import IsolationForest
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- AI CONFIG ---
metric_history = []
ai_model = IsolationForest(contamination=0.1)
AI_STATUS = "Initializing..."

PROM_CPU = Gauge('system_cpu_usage', 'CPU usage')
PROM_MEM = Gauge('system_memory_usage', 'RAM usage')
AI_GAUGE = Gauge('ai_anomaly_score', 'AI score')

def background_ai():
    global metric_history, AI_STATUS
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        PROM_CPU.set(cpu)
        PROM_MEM.set(mem)
        metric_history.append([cpu, mem])
        if len(metric_history) > 20:
            ai_model.fit(np.array(metric_history[-20:]))
            score = ai_model.predict([[cpu, mem]])[0]
            AI_STATUS = "Normal" if score == 1 else "ANOMALY!"
            AI_GAUGE.set(score)
        time.sleep(2)

threading.Thread(target=background_ai, daemon=True).start()

@app.route('/')
def index():
    log_lines = []
    try:
        # We look in the shared volume path
        with open('/usr/src/app/logs/app.log', 'r') as f:
            log_lines = f.readlines()[-10:] # Get the last 10 lines
    except Exception as e:
        log_lines = [f"Waiting for logs... (Error: {str(e)})"]
        
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
# ---------------------------------------------------------
# 2. LOGGING SETUP (The "Bridge" to Dashboard)
# ---------------------------------------------------------
logs_store = []  # <--- The Dashboard reads this list to show the table

class DashboardHandler(logging.Handler):
    """
    Custom Log Handler:
    Intercepts logs and pushes them to the 'logs_store' list 
    so the Frontend Dashboard can display them in the table.
    """
    def emit(self, record):
        try:
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            # Format: "10:00:00 | LEVEL | Message"
            log_entry = f"{timestamp} | {record.levelname} | {record.getMessage()}"
            logs_store.append(log_entry)
            # Keep list size managed
            if len(logs_store) > 100: 
                logs_store.pop(0)
        except Exception:
            self.handleError(record)

# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# A. JSON Formatter (For Console/File output - Industry Standard)
json_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(module)s')
json_handler.setFormatter(formatter)
logger.addHandler(json_handler)

# B. Dashboard Handler (For Visual UI)
dash_handler = DashboardHandler()
logger.addHandler(dash_handler)

# ---------------------------------------------------------
# 3. AI & SYSTEM MONITORING ENGINE
# ---------------------------------------------------------
current_ai_status = "GOOD"

def get_system_metrics():
    """Collects REAL system metrics using psutil"""
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "cpu": cpu,
        "memory": {"percent": mem.percent},
        "disk": {"percent": disk.percent},
        "uptime": int(time.time() - psutil.boot_time())
    }

def analyze_health(cpu, mem):
    """
    AI Logic:
    Calculates a 'Stress Score' to predict system health state.
    """
    # Weighted Score: CPU is 50% impact, RAM is 50% impact
    score = (cpu * 0.5) + (mem * 0.5)
    
    if score < 40:
        return "GOOD"     # Green
    elif score < 75:
        return "MODERATE" # Yellow
    else:
        return "CRITICAL" # Red

# ---------------------------------------------------------
# 4. FLASK ROUTES
# ---------------------------------------------------------
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Calculate latency for Prometheus
    if hasattr(request, 'start_time'):
        latency = time.time() - request.start_time
        REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
    
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

# --- DASHBOARD UI ---
@app.route('/')
def home():
    return render_template("dashboard.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

# --- DATA API (Connects Backend to Frontend) ---
@app.route('/api/data')
def api_data():
    """
    Called by dashboard.js every 2 seconds.
    Returns Metrics, Logs, and AI Decision.
    """
    metrics = get_system_metrics()
    
    # Run AI Analysis
    global current_ai_status
    current_ai_status = analyze_health(metrics['cpu'], metrics['memory']['percent'])
    
    return jsonify({
        'metrics': metrics,
        'logs': logs_store,
        'ai_status': current_ai_status
    })

# --- PROMETHEUS EXPORTER ---
@app.route('/metrics')
def metrics():
    # Update Gauges just before Prometheus scrapes
    m = get_system_metrics()
    PROM_CPU.set(m['cpu'])
    PROM_MEM.set(m['memory']['percent'])
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# --- SIMULATION ROUTES (For Demo) ---
@app.route('/api/error')
def simulate_error():
    ERROR_COUNT.labels('simulated_error').inc()
    logger.error('Simulated Critical Failure Triggered by User')
    return jsonify({'error': 'Simulated error occurred'}), 500

@app.route('/api/slow')
def slow_endpoint():
    logger.warning('Slow Database Query Detected (Simulated)')
    time.sleep(2)
    return jsonify({'message': 'Slow response completed'})

# ---------------------------------------------------------
# 5. BACKGROUND MONITOR THREAD
# ---------------------------------------------------------
def background_monitor():
    """
    Runs in the background to log system health automatically.
    This ensures logs appear even if you aren't clicking buttons.
    """
    print(" -> AI System Monitor Started...")
    while True:
        time.sleep(5)  # Check every 5 seconds
        
        try:
            stats = get_system_metrics()
            status = analyze_health(stats['cpu'], stats['memory']['percent'])
            
            # Smart Logging based on AI Status
            if status == "CRITICAL":
                logger.error(f"AI Alert: System Critical! CPU: {stats['cpu']}%")
            elif status == "MODERATE":
                logger.warning(f"AI Notice: Load Increasing. CPU: {stats['cpu']}%")
            else:
                # Randomly log 'Stable' so the log table isn't empty
                if random.random() < 0.2: 
                    logger.info(f"System Stable. AI Score: Optimal")
                    
        except Exception as e:
            print(f"Monitor Error: {e}")

if __name__ == '__main__':
    # Start the Background AI Thread
    t = threading.Thread(target=background_monitor, daemon=True)
    t.start()
    
    # Run the App (Host 0.0.0.0 is required for Docker)
    print("SYSTEM ONLINE: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)