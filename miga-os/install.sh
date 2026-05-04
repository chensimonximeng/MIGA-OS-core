#!/bin/bash
# MIGA-OS "Internal" Installer

if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit
fi

echo "Installing MIGA-OS from internal directory..."

# 1. Create System Directories
mkdir -p /etc/miga
mkdir -p /usr/bin/miga-core

# 2. Move the Python logic 
# We removed "miga-os/" from the start because the script is now INSIDE that folder
cp usr/bin/*.py /usr/bin/miga-core/

# 3. Move the System Services
cp etc/systemd/system/*.service /etc/systemd/system/

# 4. Finalize the System
systemctl daemon-reload
systemctl enable miga-monitor.service
systemctl enable miga-power-init.service
systemctl start miga-monitor.service

echo "MIGA-OS Installation Complete."
