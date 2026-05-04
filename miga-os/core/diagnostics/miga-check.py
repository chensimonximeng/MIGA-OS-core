import curses
import time
import os

def get_val(path, divide=1000):
    """Helper to read sysfs values safely."""
    try:
        with open(path, 'r') as f:
            return int(f.read()) / divide
    except: return 0

def draw_dashboard(stdscr):
    # Hide the cursor
    curses.curs_set(0)
    # Set a non-blocking refresh rate (1 second)
    stdscr.nodelay(True)
    stdscr.timeout(1000)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # --- DATA GATHERING ---
        temp = get_val("/sys/class/thermal/thermal_zone0/temp")
        # Power usage in Watts (micro-watts to Watts)
        power = get_val("/sys/class/powercap/intel-rapl:0/energy_uj", 1000000) 
        # Note: RAPL energy is a counter, for live Watts we'd need a delta, 
        # but let's show the Power Limit 1 (PL1) instead for now:
        pl1 = get_val("/sys/class/powercap/intel-rapl:0/constraint_0_power_limit_uw", 1000000)
        
        # --- UI DRAWING ---
        stdscr.attron(curses.A_BOLD | curses.color_pair(1))
        stdscr.addstr(0, 0, " MIGA-OS HARDWARE DIAGNOSTIC ")
        stdscr.attroff(curses.A_BOLD)

        stdscr.addstr(2, 0, f"CPU Temperature:   {temp:>6.1f} °C")
        
        # Draw a simple thermal bar
        bar_width = int((temp / 100) * 20)
        stdscr.addstr(2, 30, "[" + ("#" * bar_width) + ("-" * (20 - bar_width)) + "]")

        stdscr.addstr(3, 0, f"Current PL1 Limit: {pl1:>6.1f} W")
        
        # Status Section
        stdscr.addstr(5, 0, "--- System Health ---")
        status = "HEALTHY" if temp < 80 else "CRITICAL"
        stdscr.addstr(6, 0, f"Thermal Status:    {status}")
        
        stdscr.addstr(height-1, 0, "Press 'q' to exit MIGA-Check")

        # Check for quit key
        key = stdscr.getch()
        if key == ord('q'):
            break

        stdscr.refresh()

if __name__ == "__main__":
    # Initialize color and run the dashboard
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(draw_dashboard)
