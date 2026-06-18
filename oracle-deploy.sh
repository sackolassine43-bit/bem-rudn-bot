#!/bin/bash
# Déploiement sur Oracle Cloud Always Free (Ubuntu VM)

sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y

git clone https://github.com/sackolassine43-bit/bem-rudn-bot.git
cd bem-rudn-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Créer le service systemd pour 24/7
sudo cat > /etc/systemd/system/bem-rudn.service << 'EOF'
[Unit]
Description=BEM-RUDN Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/bem-rudn-bot
ExecStart=/home/ubuntu/bem-rudn-bot/venv/bin/python3 src/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable bem-rudn
sudo systemctl start bem-rudn
echo "✅ Bot démarré 24/7 sur Oracle Cloud"
