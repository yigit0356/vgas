#!/bin/bash

set -e

echo "--- System updating ---"
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git python3-pip python3-venv network-manager curl

echo "--- Balena-os/wifi-connect is installing ---"
curl -L https://github.com/balena-os/wifi-connect/releases/download/v4.11.1/wifi-connect-linux-rpi.tar.gz | tar -xvz
sudo mv wifi-connect /usr/local/bin/

echo "--- Repo is being cloned ---"
PROJECT_DIR="$HOME/vgas_project"
mkdir -p $PROJECT_DIR
git clone https://github.com/yigit0356/vgas $PROJECT_DIR/repo

echo "--- Python virtual environment and dependencies are being prepared ---"
cd $PROJECT_DIR/repo/controller
python3 -m venv venv
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "requirements.txt found, dependencies are being installed..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found, dependency installation skipped."
fi

deactivate

echo "--- Systemd services are being created ---"

sudo bash -c "cat <<EOF > /etc/systemd/system/wifi-connect.service
[Unit]
Description=Wireless Connect Captive Portal
After=network-manager.service

[Service]
Type=simple
ExecStart=/usr/local/bin/wifi-connect -u /usr/local/share/wifi-connect/ui
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

DEVICE_NAME=$(hostname)

sudo bash -c "cat <<EOF > /etc/systemd/system/vgas-controller.service
[Unit]
Description=VGAS Setup ($DEVICE_NAME)
After=network.target wifi-connect.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/repo/controller
ExecStart=$PROJECT_DIR/repo/controller/venv/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

echo "--- Services are being activated ---"
sudo systemctl daemon-reload
sudo systemctl enable wifi-connect.service
sudo systemctl enable vgas-controller.service

echo "-----------------------------------------------------------------"
echo "Setup is complete! It is recommended that you restart the device."
echo "-----------------------------------------------------------------"
