import os
import time
import subprocess
import glob

class MigaMonitor:
    def __init__(self):
        self.temp_high = 85   # Trigger downscale
        self.temp_low = 75    # Allow upscale (Hysteresis)
        self.poll_rate = 2 
        self.is_throttled = False
        
        # Determine the directory of THIS script to call the daemon correctly
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.daemon_path = os.path.join(self.base_dir, "miga-power-daemon.py")
        
        # Dynamic Power Supply Detection
        self.ac_path = self._find_ac_path()

    def _find_ac_path(self):
        """Finds the AC power path regardless of the laptop brand."""
        paths = glob.glob("/sys/class/power_supply/*/online")
        for p in paths:
            if "AC" in p or "ADP" in p or "acad" in p:
                return p
        return None

    def get_cpu_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return int(f.read()) / 1000
        except: return 0

    def check_power_source(self):
        if not self.ac_path: return "unknown"
        try:
            with open(self.ac_path, "r") as f:
                return "ac" if f.read().strip() == "1" else "battery"
        except: return "unknown"

    def run(self):
        print(f"MIGA-Monitor: System active. AC Path: {self.ac_path}")
        last_source = None
        
        while True:
            temp = self.get_cpu_temp()
            source = self.check_power_source()

            # --- LOGIC 1: SMART THERMAL MANAGEMENT ---
            if temp > self.temp_high and not self.is_throttled:
                print(f"THERMAL OVERRIDE: {temp}C. Downscaling.")
                subprocess.run(["python3", self.daemon_path, "efficiency"])
                self.is_throttled = True
            
            elif temp < self.temp_low and self.is_throttled:
                print(f"THERMAL RECOVERY: {temp}C. Returning to normal logic.")
                self.is_throttled = False
                last_source = None # Force a re-check of power source

            # --- LOGIC 2: POWER SOURCE AUTO-SWITCHING ---
            if not self.is_throttled and source != last_source:
                if source == "battery":
                    subprocess.run(["python3", self.daemon_path, "efficiency"])
                elif source == "ac":
                    subprocess.run(["python3", self.daemon_path, "nitro"])
                last_source = source

            time.sleep(self.poll_rate)

if __name__ == "__main__":
    monitor = MigaMonitor()
    monitor.run()
