import tkinter as tk
import subprocess

def set_nitro():
    subprocess.run(["python3", "/usr/bin/miga-core/miga-power-daemon.py", "nitro"])
    status_label.config(text="Mode: NITRO (Max Performance)", fg="orange")

def set_eco():
    subprocess.run(["python3", "/usr/bin/miga-core/miga-power-daemon.py", "efficiency"])
    status_label.config(text="Mode: ECO (Battery Saver)", fg="green")

root = tk.Tk()
root.title("MIGA-OS Power Control")
root.geometry("300x200")

label = tk.Label(root, text="Select Power Profile", font=("Arial", 12))
label.pack(pady=10)

tk.Button(root, text="NITRO MODE", command=set_nitro, width=20, bg="orange").pack(pady=5)
tk.Button(root, text="ECO MODE", command=set_eco, width=20, bg="lightgreen").pack(pady=5)

status_label = tk.Label(root, text="Mode: Auto-Monitoring", fg="gray")
status_label.pack(pady=10)

root.mainloop()
