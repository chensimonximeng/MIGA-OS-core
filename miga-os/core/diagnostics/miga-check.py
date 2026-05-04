import curses
import time
import os

class MigaCheck:
    def __init__(self):
        self.rapl_energy_path = "/sys/class/powercap/intel-rapl:0/energy_uj"
        self.rapl_limit_path = "/sys/class/powercap/intel-rapl:0/constraint_0_power_limit_uw"
        self.temp_path = "/sys/class/thermal/thermal_zone0/temp"

    def get_val(self, path):
        try:
            with open(path, 'r') as f: return int(f.read())
        except: return 0

    def get_live_watts(self):
        """Calculates energy delta over time to get real-time Wattage."""
        e1 = self.get_val(self.rapl_energy_path)
        time.sleep(0.5) # Sample window
        e2 = self.get_val(self.rapl_energy_path)
        # (microjoules delta) / (0.5 seconds) / 1,000,000 = Watts
        return ((e2 - e1) / 0.5) / 1000000

    def draw(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        while True:
            stdscr.clear()
            
            # Data
            temp = self.get_val(self.temp_path) / 1000
            watts = self.get_live_watts()
            limit = self.get_val(self.rapl_limit_path) / 1000000

            # Display
            stdscr.addstr(0, 0, "=== MIGA-OS LIVE DIAGNOSTICS ===", curses.A_REVERSE)
            stdscr.addstr(2, 0, f"THERMAL: {temp:>5.1f} °C")
            stdscr.addstr(3, 0, f"DRAIN:   {watts:>5.2f} W (Real-time)")
            stdscr.addstr(4, 0, f"LIMIT:   {limit:>5.1f} W (Active Profile)")
            
            stdscr.addstr(6, 0, "Press 'q' to exit")
            if stdscr.getch() == ord('q'): break
            stdscr.refresh()

if __name__ == "__main__":
    diag = MigaCheck()
    curses.wrapper(diag.draw)
