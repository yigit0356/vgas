#!/bin/bash

REPO_URL="https://github.com/yigit0356/vgas.git"
TARGET_DIR="$HOME/vgas"
SUBFOLDER="controller"
SERVICE_NAME="vgas"
PYTHON_EXE="/usr/bin/python3"

echo "=== Custom Setup Starting ==="

sudo apt update && sudo apt install -y python3 python3-pip git

echo "WI-FI is expected..."
until ping -c 1 google.com &>/dev/null; do sleep 5; done

TEMP_DIR=$(mktemp -d)
echo "Repo is being temporarily downloaded to the $TEMP_DIR directory...."
git clone $REPO_URL $TEMP_DIR

if [ -d "$TEMP_DIR/$SUBFOLDER" ]; then
    echo "Target folder ($SUBFOLDER) has been found and is being moved...."
    mkdir -p $TARGET_DIR
    cp -r $TEMP_DIR/$SUBFOLDER/. $TARGET_DIR/
    rm -rf $TEMP_DIR
else
    echo "ERROR: The ‘$SUBFOLDER’ folder could not be found in the repository."
    exit 1
fi

cd $TARGET_DIR
if [ -f "requirements.txt" ]; then
    echo "Dependencies are loading..."
    pip3 install -r requirements.txt
fi

echo "System service is being created..."
sudo bash -c "cat <<EOT > /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=VGAS Setup
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$TARGET_DIR
ExecStart=$PYTHON_EXE $TARGET_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOT"

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service
sudo systemctl restart $SERVICE_NAME.service

echo "=== Process Complete ==="
echo "Project path: $TARGET_DIR"
echo "Service status: $(sudo systemctl is-active $SERVICE_NAME)"
