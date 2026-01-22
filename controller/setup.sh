#!/bin/bash

# VGAS Controller - Raspberry Pi Setup Script
# Bu script Raspberry Pi üzerinde projeyi kurar, servisleri yapılandırır ve başlatır.

set -e

echo "--- [1/6] Sistem paketleri güncelleniyor ve bağımlılıklar kuruluyor ---"
sudo apt-get update
sudo apt-get install -y git python3-pip python3-venv python3-dev \
    network-manager curl \
    libjpeg-dev zlib1g-dev \
    libsdl2-2.0-0 libsdl2-mixer-2.0-0 \
    portaudio19-dev

echo "--- [2/6] Wifi-Connect (Captive Portal) kuruluyor ---"
# Wifi-connect, cihazın Wi-Fi ayarlarını telefon üzerinden yapmanızı sağlar
if [ ! -f "/usr/local/bin/wifi-connect" ]; then
    echo "Wifi-connect indiriliyor..."
    # v4.4.6 Raspberry Pi (armv7hf) için uyumlu sürümdür
    WIFI_CONNECT_VERSION="4.4.6"
    WIFI_CONNECT_URL="https://github.com/balena-os/wifi-connect/releases/download/v$WIFI_CONNECT_VERSION/wifi-connect-v$WIFI_CONNECT_VERSION-linux-armv7hf.tar.gz"
    
    if curl -L "$WIFI_CONNECT_URL" | tar -xvz; then
        sudo mv wifi-connect /usr/local/bin/
        echo "Wifi-connect başarıyla kuruldu."
    else
        echo "UYARI: Wifi-connect indirilemedi. Bu adım atlanıyor, kurulum devam ediyor..."
    fi
fi

echo "--- [3/6] Proje dizini ve Python ortamı hazırlanıyor ---"
PROJECT_DIR="$HOME/vgas_project"
mkdir -p $PROJECT_DIR

# Eğer repo zaten yoksa klonla, varsa güncelle
if [ ! -d "$PROJECT_DIR/vgas" ]; then
    git clone https://github.com/yigit0356/vgas $PROJECT_DIR/vgas
else
    cd $PROJECT_DIR/vgas
    git pull
fi

cd $PROJECT_DIR/vgas/controller

# Sanal ortam oluşturma
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Bağımlılıkları yükle
source venv/bin/activate
echo "Python bağımlılıkları yükleniyor (bu biraz zaman alabilir)..."
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Varsayılan config.json oluştur
if [ ! -f "config.json" ]; then
    echo '{"api_key": ""}' > config.json
    echo "Varsayılan config.json oluşturuldu."
fi

echo "--- [4/6] Systemd servisleri yapılandırılıyor ---"

# 1. Wifi-Connect Servisi
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

# 2. VGAS Controller Servisi
DEVICE_NAME=$(hostname)
sudo bash -c "cat <<EOF > /etc/systemd/system/vgas-controller.service
[Unit]
Description=VGAS Controller Service ($DEVICE_NAME)
After=network.target wifi-connect.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/vgas/controller
ExecStart=$PROJECT_DIR/vgas/controller/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo "--- [5/6] Servisler aktifleştiriliyor ---"
sudo systemctl daemon-reload
sudo systemctl enable wifi-connect.service
sudo systemctl enable vgas-controller.service

echo "--- [6/6] Kurulum tamamlandı! ---"
echo "-----------------------------------------------------------------"
echo "Sistemi yeniden başlatmanız önerilir: sudo reboot"
echo "Dashboard adresi: http://$(hostname -I | awk '{print $1}'):8000"
echo "-----------------------------------------------------------------"
