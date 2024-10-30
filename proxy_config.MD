# Create systemd service file
sudo nano /etc/systemd/system/proxy-server.service

[Unit]
Description=Python Proxy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/python/proxy-server
Environment=PATH=/var/python/proxy-server/venv/bin:$PATH
ExecStart=/var/python/proxy-server/venv/bin/python /var/python/proxy-server/proxy_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target