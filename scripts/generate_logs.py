import random
import time
import json
import socket
from datetime import datetime
import requests
import sys

# Inside your generate_log_message loop or function:
def generate_log_message():
    # ... [keep existing lists]
    
    # AI Test: 5% chance to generate a massive burst of errors (Anomaly)
    if random.random() < 0.05:
        return {
            "timestamp": datetime.now().isoformat(),
            "level": "CRITICAL",
            "service": "AI-ANOMALY-TEST",
            "message": "SIMULATED ATTACK: Multiple failed login attempts detected",
            "code": 500
        }
    
    level = random.choice(log_levels)
    service = random.choice(services)
    message = random.choice(messages.get(level, ['Unknown event']))
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'service': service,
        'message': message,
        'host': socket.gethostname(),
        'user_id': f'user_{random.randint(1000, 9999)}',
        'session_id': f'session_{random.randint(10000, 99999)}',
        'duration_ms': random.randint(10, 5000) if level in ['INFO', 'DEBUG'] else random.randint(5000, 30000),
        'status_code': 200 if level == 'INFO' else 500 if level in ['ERROR', 'CRITICAL'] else random.choice([200, 201, 400, 401, 403, 404, 500])
    }
    
    return log_entry

def send_to_logstash(log_entry):
    try:
        # Send to Logstash TCP input
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5000))
        sock.sendall((json.dumps(log_entry) + '\n').encode())
        sock.close()
        return True
    except Exception as e:
        print(f"Error sending to Logstash: {e}")
        return False

def send_to_prometheus():
    try:
        # Simulate metrics for Prometheus
        metrics = {
            'cpu_usage': random.uniform(10, 90),
            'memory_usage': random.uniform(30, 85),
            'disk_usage': random.uniform(40, 95),
            'request_rate': random.randint(100, 1000),
            'error_rate': random.uniform(0.1, 5.0)
        }
        
        # In a real scenario, you'd use Prometheus client library
        # For demo, we'll just print
        return True
    except Exception as e:
        print(f"Error with metrics: {e}")
        return False

def main():
    print("Starting log generation...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Generate log
            log_entry = generate_log_message()
            
            # Send to Logstash
            if send_to_logstash(log_entry):
                print(f"Sent: {log_entry['level']} - {log_entry['message']}")
            
            # Send metrics (simulated)
            send_to_prometheus()
            
            # Wait before next log
            delay = random.uniform(0.1, 2.0)
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\nStopping log generation...")
        sys.exit(0)

if __name__ == "__main__":
    main()