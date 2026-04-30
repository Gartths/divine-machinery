#!/usr/bin/env python3
"""
ESP32 System Monitor - PC Server
Sends CPU/GPU/RAM stats to ESP32 via HTTP JSON

Requirements:
pip install flask psutil py-cpuinfo GPUtil flask-cors

Or minimal version (without GPU):
pip install flask psutil flask-cors
"""

import json
import psutil
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime
import socket

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

# Try to import optional dependencies
try:
    import cpuinfo
    HAS_CPUINFO = True
except ImportError:
    HAS_CPUINFO = False
    print("[WARNING] py-cpuinfo not installed. Install with: pip install py-cpuinfo")

try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
    print("[WARNING] GPUtil not installed. GPU temps will be 0. Install with: pip install GPUtil")

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
        print(f"[WARNING] CPU Temp not available: {e}")
        return 0.0

# ==================== GET GPU TEMPERATURE ====================
def get_gpu_temp():
    """Get GPU temperature (NVIDIA only)"""
    if not HAS_GPU:
        return 0.0
    
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return float(gpus[0].temperature)
        return 0.0
    except Exception as e:
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

# ==================== GET CPU INFO ====================
def get_cpu_name():
    """Get CPU name"""
    if HAS_CPUINFO:
        try:
            return cpuinfo.get_cpu_info()['brand_raw']
        except:
            pass
    
    # Fallback
    return "Unknown CPU"

# ==================== GET HOSTNAME ====================
def get_hostname():
    """Get computer hostname"""
    try:
        return socket.gethostname()
    except:
        return "Unknown"

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
            "cpu": get_cpu_name(),
            "ram_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "hostname": get_hostname()
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
    print("\n" + "="*70)
    print(" 🖥️  ESP32 System Monitor - PC Server")
    print("="*70)
    
    # Print system info
    try:
        print(f"\n📊 System Information:")
        print(f"   CPU: {get_cpu_name()}")
        print(f"   RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"   Hostname: {get_hostname()}")
        
        # Check GPU
        if HAS_GPU:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    print(f"   GPU: {gpus[0].name}")
                else:
                    print(f"   GPU: Not found")
            except:
                print(f"   GPU: Not available")
        else:
            print(f"   GPU: GPUtil not installed")
    except Exception as e:
        print(f"[WARNING] Could not get system info: {e}")
    
    # Start background thread
    print(f"\n🚀 Starting stats thread...")
    thread = threading.Thread(target=update_stats_thread, daemon=True)
    thread.start()
    
    # Get local IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    
    # Start Flask server
    print(f"\n📡 Starting HTTP server...")
    print(f"   Local:    http://127.0.0.1:{PORT}/stats")
    print(f"   Network:  http://{local_ip}:{PORT}/stats")
    print(f"\n   Available endpoints:")
    print(f"   • /stats  - Get system stats (JSON)")
    print(f"   • /info   - Get system info")
    print(f"   • /health - Health check")
    print(f"\n💡 Configure ESP32 with your PC IP address:")
    print(f"   const char* serverURL = \"http://{local_ip}:{PORT}/stats\";")
    print("="*70 + "\n")
    
    # Run Flask app
    try:
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
