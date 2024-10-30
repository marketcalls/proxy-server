#!/bin/bash

# Preserve existing rules for SSH, Nginx, and Redis
# Add proxy server rules while maintaining current configuration

# Add proxy server port (adjust if needed)
sudo ufw allow 8080/tcp comment 'Proxy Server'

# Allow outgoing web traffic (if not already allowed)
sudo ufw allow out 80/tcp comment 'Proxy HTTP outbound'
sudo ufw allow out 443/tcp comment 'Proxy HTTPS outbound'

# Optional: Limit proxy access to specific IP ranges (uncomment and modify as needed)
# sudo ufw allow from 192.168.1.0/24 to any port 8080 proto tcp comment 'Proxy LAN access'

# Reload UFW to apply changes
sudo ufw reload

# Show updated status
sudo ufw status verbose
