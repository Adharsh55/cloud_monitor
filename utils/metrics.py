import psutil
import time

def get_system_metrics():
    """Collects raw OS data for the app"""
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": cpu,
        "memory": {"percent": mem.percent},
        "disk": {"percent": disk.percent},
        "uptime": int(time.time() - psutil.boot_time())
    }