#!/usr/bin/env python3
"""
ESP32 System Monitor - PC Server
Sends CPU/GPU/RAM stats to ESP32 via HTTP JSON

Requirements:
pip install flask psutil py-cpuinfo GPUtil
"""

import json
import psutil
import cpuinfo
import GPUtil
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==================== CONFIG ====================
HOST = "0.0.0.0"  # Accessible from network
PORT = 5000
UPDATE_INTERVAL = 1  # seconds

# ==================== GLOBAL STATS ====================
stats = {
    "cpu_temp": 0.0,
    "gpu_temp": 0.0,
    "cpu_load": 0.0,
    "ram_usage": 0.0,
    "timestamp": ""
}

# ==================== GET CPU TEMPERATURE ====================
def get_cpu_temp():
    """Get CPU temperature"""
    try:
        temps = psutil.sensors_temperatures()
        
        # Try to get from common sources
        if 'coretemp' in temps:  # Intel
            return temps['coretemp'][0].current
        elif 'k10temp' in temps:  # AMD
            return temps['k10temp'][0].current
        elif 'acpitz' in temps:  # Alternative
            return temps['acpitz'][0].current
        else:
            # Return first available
            for name, entries in temps.items():
                if entries:
                    return entries[0].current
        return 0.0
    except Exception as e:
        print(f"[ERROR] CPU Temp: {e}")
        return 0.0

# ==================== GET GPU TEMPERATURE ====================
def get_gpu_temp():
    """Get GPU temperature (NVIDIA only)"""
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return float(gpus[0].temperature)
        return 0.0
    except Exception as e:
        print(f"[WARNING] GPU Temp not available: {e}")
        return 0.0

# ==================== GET CPU LOAD ====================
def get_cpu_load():
    """Get CPU load percentage"""
    try:
        return psutil.cpu_percent(interval=0.1)
    except Exception as e:
        print(f"[ERROR] CPU Load: {e}")
        return 0.0

# ==================== GET RAM USAGE ====================
def get_ram_usage():
    """Get RAM usage percentage"""
    try:
        return psutil.virtual_memory().percent
    except Exception as e:
        print(f"[ERROR] RAM Usage: {e}")
        return 0.0

# ==================== UPDATE STATS THREAD ====================
def update_stats_thread():
    """Background thread to update stats"""
    global stats
    
    while True:
        try:
            stats = {
                "cpu_temp": round(get_cpu_temp(), 2),
                "gpu_temp": round(get_gpu_temp(), 2),
                "cpu_load": round(get_cpu_load(), 1),
                "ram_usage": round(get_ram_usage(), 1),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] CPU: {stats['cpu_temp']}°C | "
                  f"GPU: {stats['gpu_temp']}°C | "
                  f"CPU Load: {stats['cpu_load']}% | "
                  f"RAM: {stats['ram_usage']}%")
            
        except Exception as e:
            print(f"[ERROR] Update stats: {e}")
        
        time.sleep(UPDATE_INTERVAL)

# ==================== API ENDPOINT ====================
@app.route('/stats', methods=['GET'])
def get_stats():
    """Return system stats as JSON"""
    return jsonify(stats)

# ==================== API ENDPOINT - INFO ====================
@app.route('/info', methods=['GET'])
def get_info():
    """Return system info"""
    try:
        info = {
            "cpu": cpuinfo.get_cpu_info()['brand_raw'],
            "ram_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "hostname": __import__('socket').gethostname()
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== API ENDPOINT - HEALTH ====================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "OK", "version": "1.0"}), 200

# ==================== MAIN ====================
if __name__ == '__main__':
    print("\n" + "="*60)
    print(" ESP32 System Monitor - PC Server")
    print("="*60)
    
    # Print system info
    try:
        print(f"\n📊 System Information:")
        print(f"   CPU: {cpuinfo.get_cpu_info()['brand_raw']}")
        print(f"   RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"   Hostname: {__import__('socket').gethostname()}")
        
        # Check GPU
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                print(f"   GPU: {gpus[0].name}")
            else:
                print(f"   GPU: Not found")
        except:
            print(f"   GPU: Not available")
    except Exception as e:
        print(f"[WARNING] Could not get system info: {e}")
    
    # Start background thread
    print(f"\n🚀 Starting stats thread...")
    thread = threading.Thread(target=update_stats_thread, daemon=True)
    thread.start()
    
    # Start Flask server
    print(f"\n📡 Starting HTTP server...")
    print(f"   Address: http://0.0.0.0:{PORT}")
    print(f"   Endpoint: /stats (JSON data)")
    print(f"   Endpoint: /info (System info)")
    print(f"   Endpoint: /health (Health check)")
    print(f"\n💡 Configure ESP32 with your PC IP address!")
    print(f"   Example: http://192.168.1.X:{PORT}/stats")
    print("="*60 + "\n")
    
    # Run Flask app
    try:
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
