import logging
import os
import re
import sys  # <--- NEW IMPORT
from logging.handlers import RotatingFileHandler

# Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

def sanitize_log(message):
    sensitive_keywords = ["password", "token", "secret", "key"]
    for keyword in sensitive_keywords:
        message = re.sub(f"{keyword}=\\S+", f"{keyword}=***", message, flags=re.IGNORECASE)
    return message

# -------------------------------
# UPDATED LOGGER SETUP
# -------------------------------
logger = logging.getLogger("cloud_monitor")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

# 1. File Handler (Saves to file)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 2. Console Handler (Prints to Terminal) <--- THIS IS THE FIX
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def log(level, message):
    safe_message = sanitize_log(message)
    if level.lower() == "info":
        logger.info(safe_message)
    elif level.lower() == "warning":
        logger.warning(safe_message)
    elif level.lower() == "error":
        logger.error(safe_message)
    else:
        logger.info(safe_message)

def read_last_logs(n=50):
    if not os.path.exists(LOG_FILE):
        return ["Waiting for logs..."]
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return lines[-n:] if lines else ["System initialized..."]
    except:
        return []