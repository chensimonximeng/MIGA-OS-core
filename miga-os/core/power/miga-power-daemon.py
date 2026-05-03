import os
import json
import sys

class MigaPowerDaemon:
    def __init__(self):
        self.config_path = "/etc/miga/power_profiles.json"
        self.cpu_path = "/sys/devices/system/cpu"
        
        # Hardware-specific paths
        self.rapl_path = "/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw"
        self.rockchip_path = "/sys/class/thermal/cooling_device0/cur_state" # Example for ARM
        
        # Initialize
        self.total_cores = os.cpu_count()
        self.ensure_config_exists()

    def ensure_config_exists(self):
        """Creates the customizable profile map if it doesn't exist."""
        if not os.path.exists(self.config_path):
            os.makedirs("/etc/miga/", exist_ok=True)
            # This is where the user 'designs' their modes
            default_map = {
                "hardware_info": {"detected_cores": self.total_cores},
                "safety_limits": {"max_watts": 100, "min_volts_offset": -100},
                "profiles": {
                    "nitro": {
                        "active_cores": list(range(self.total_cores)),
                        "watts": 65,
                        "governor": "performance",
                        "uv_offset": 0
                    },
                    "efficiency": {
                        "active_cores": [0, 1, 2, 3], 
                        "watts": 15,
                        "governor": "powersave",
                        "uv_offset": -50
                    }
                }
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_map, f, indent=4)

    def apply_profile(self, profile_name):
        """Executes the user's custom design onto the silicon."""
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        
        if profile_name not in data["profiles"]:
            print(f"Mode {profile_name} not found in profiles.json")
            return

        config = data["profiles"][profile_name]
        limits = data.get("safety_limits", {"max_watts": 65})

        # --- 1. SAFETY CHECK ---
        requested_watts = min(config["watts"], limits["max_watts"])

        # --- 2. CORE CUSTOMIZATION ---
        # User defines which cores to keep; we kill the rest.
        for i in range(1, self.total_cores): 
            status = "1" if i in config["active_cores"] else "0"
            self._write_file(f"{self.cpu_path}/cpu{i}/online", status)

        # --- 3. WATTAGE CONTROL (Intel/AMD/Universal) ---
        if os.path.exists(self.rapl_path):
            self._write_file(self.rapl_path, requested_watts * 1000000)
        
        # --- 4. GOVERNOR & UNDERVOLT ---
        # Note: True undervolting requires 'msr-tools' for x86 or 'i2c-tools' for ARM.
        # This acts as the hook for those commands.
        for i in range(self.total_cores):
            gov_path = f"{self.cpu_path}/cpu{i}/cpufreq/scaling_governor"
            if os.path.exists(gov_path):
                self._write_file(gov_path, config["governor"])
        
        print(f"MIGA-OS: Mode '{profile_name}' applied. Power Cap: {requested_watts}W")

    def _write_file(self, path, value):
        try:
            with open(path, 'w') as f:
                f.write(str(value))
        except:
            pass 

if __name__ == "__main__":
    daemon = MigaPowerDaemon()
    # If user runs 'miga-power-daemon.py gaming', it applies that profile
    mode = sys.argv[1] if len(sys.argv) > 1 else "nitro"
    daemon.apply_profile(mode)
