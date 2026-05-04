import os
import time
import subprocess

class MigaMonitor:
    def __init__(self):
        self.temp_threshold = 85  # Celsius (Safe for 3D prints)
        self.poll_rate = 2        # Seconds
        
    def get_cpu_temp(self):
        """Reads the primary thermal zone."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return int(f.read()) / 1000
        except: return 0

    def check_power_source(self):
        """Detects if we are on AC or Battery."""
        try:
            with open("/sys/class/power_supply/AC/online", "r") as f:
                return "ac" if f.read().strip() == "1" else "battery"
        except: return "unknown"

    def run(self):
        print("MIGA-Monitor: Monitoring hardware vitals...")
        last_source = None
        
        while True:
            temp = self.get_cpu_temp()
            source = self.check_power_source()

            # LOGIC 1: Emergency Thermal Override
            if temp > self.temp_threshold:
                print(f"ALERT: Temp at {temp}C! Triggering Emergency Efficiency Mode.")
                subprocess.run(["python3", "miga-power-daemon.py", "efficiency"])

            # LOGIC 2: Auto-Switching based on Plug
            if source != last_source:
                if source == "battery":
                    print("Switching to Efficiency (Battery Detected)")
                    subprocess.run(["python3", "miga-power-daemon.py", "efficiency"])
                elif source == "ac":
                    print("Switching to Nitro (AC Power Detected)")
                    subprocess.run(["python3", "miga-power-daemon.py", "nitro"])
                last_source = source

            time.sleep(self.poll_rate)

if __name__ == "__main__":
    monitor = MigaMonitor()
    monitor.run()
