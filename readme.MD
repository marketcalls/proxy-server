# Python Proxy Server

A lightweight HTTP/HTTPS proxy server implementation in Python with comprehensive monitoring and testing capabilities.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running as a Service](#running-as-a-service)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Windows Client Setup](#windows-client-setup)
- [Troubleshooting](#troubleshooting)

## Features
- HTTP and HTTPS proxy support
- Real-time monitoring dashboard
- System resource monitoring
- Connection tracking
- Automated testing
- UFW firewall configuration
- Systemd service integration
- Log rotation
- Detailed error logging

## Project Structure
```plaintext
/var/python/proxy-server/
├── proxy_server.py        # Main proxy server implementation
├── dashboard.sh           # Interactive monitoring dashboard
├── monitor.sh             # System monitoring script
├── test_proxy.sh          # Proxy testing script
├── ufw_config.sh          # UFW firewall configuration
├── README.MD              # This file
├── proxy_config.MD        # Service configuration instructions
├── LICENSE                # MIT License file
├── .gitignore             # Git ignore file
├── venv/                  # Python virtual environment
└── logs/                  # Log directory
    ├── access.log         # Access logs
    ├── error.log          # Error logs
    └── proxy.log          # General proxy logs
```

## Prerequisites
- Ubuntu Server 22.04 LTS or later
- Python 3.8+
- UFW (Uncomplicated Firewall)
- Root or sudo access
- Git

## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/marketcalls/proxy-server.git
cd proxy-server
```

2. **Update System and Install Dependencies**
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip net-tools ufw
```

3. **Set Up Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

4. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

5. **Set Proper Permissions**
```bash
chmod +x proxy_server.py dashboard.sh monitor.sh test_proxy.sh ufw_config.sh
chmod 644 README.MD proxy_config.MD LICENSE .gitignore
chmod 755 logs
chmod 640 logs/*.log
```

## Configuration

1. **Configure UFW Firewall**
```bash
# Configure UFW
./ufw_config.sh

# Verify UFW status
sudo ufw status
```

2. **Configure Log Rotation**
```bash
# Create log files if they don't exist
touch logs/{access,error,proxy}.log
chmod 640 logs/*.log
```

## Running as a Service

1. **Create Systemd Service**
```bash
# Create service file (content in proxy_config.MD)
sudo nano /etc/systemd/system/proxy-server.service
```

2. **Enable and Start Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable proxy-server

# Start service
sudo systemctl start proxy-server

# Check status
sudo systemctl status proxy-server
```

3. **Service Management Commands**
```bash
# Stop service
sudo systemctl stop proxy-server

# Restart service
sudo systemctl restart proxy-server

# View logs
sudo journalctl -u proxy-server -f
```

## Monitoring

1. **Using Dashboard**
```bash
# Start monitoring dashboard
./dashboard.sh
```

2. **Using Monitor Script**
```bash
# Run system monitor
./monitor.sh
```

3. **View Logs**
```bash
# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log

# Proxy logs
tail -f logs/proxy.log
```

## Testing

1. **Run Test Suite**
```bash
# Execute test script
./test_proxy.sh
```

2. **Manual Testing**
```bash
# Test HTTP
curl -v -x http://localhost:8080 http://example.com

# Test HTTPS
curl -v -x http://localhost:8080 https://example.com
```

## Windows Client Setup

### Method 1: Windows Settings
1. Open Windows Settings (Win + I)
2. Navigate to Network & Internet → Proxy
3. Under "Manual proxy setup":
   - Enable "Use a proxy server"
   - Address: Your Server IP
   - Port: 8080
   - Click Save

### Method 2: PowerShell
```powershell
# Run as Administrator
$proxy = "http://YOUR_SERVER_IP:8080"
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -Value $proxy
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 1
```

## Troubleshooting

### Server Issues

1. **Service Won't Start**
```bash
# Check service status
sudo systemctl status proxy-server

# Check logs
sudo journalctl -u proxy-server -e
```

2. **Connection Issues**
```bash
# Check if proxy is running
ps aux | grep proxy_server.py

# Check open ports
netstat -tulpn | grep 8080

# Check UFW status
sudo ufw status
```

### Client Issues

1. **Can't Connect**
- Verify proxy settings
- Check firewall settings
- Try using curl to test connection
- Clear DNS cache: `ipconfig /flushdns`

2. **SSL Issues**
- Clear SSL state: `certutil -URLCache * delete`
- Verify HTTPS support
- Check proxy logs for errors

## Daily Maintenance

1. **Morning Checks**
```bash
# Check service status
sudo systemctl status proxy-server

# View dashboard
./dashboard.sh

# Check logs
tail -n 100 logs/error.log
```

2. **Evening Checks**
```bash
# Check connections
netstat -ant | grep :8080 | wc -l

# View monitoring data
./monitor.sh
```

## Security Recommendations

1. **Basic Security**
- Keep system updated
- Monitor logs regularly
- Use proper firewall rules
- Implement authentication if needed

2. **Access Control**
- Limit access by IP if possible
- Monitor connection attempts
- Review logs for suspicious activity

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Feel free to submit issues and pull requests.
