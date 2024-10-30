#!/bin/bash

echo "=== System Status Report ==="
date
echo

echo "=== UFW Status ==="
sudo ufw status verbose
echo

echo "=== Active Services ==="
systemctl status nginx | grep Active
systemctl status redis | grep Active
echo

echo "=== Proxy Server Status ==="
if pgrep -f "proxy_server.py" > /dev/null
then
    echo "Proxy Server: Running"
    echo "Proxy Server Process Info:"
    ps aux | grep "[p]roxy_server.py"
    echo
    echo "Proxy Server Connections:"
    netstat -ant | grep :8080
else
    echo "Proxy Server: Not Running"
fi
echo

echo "=== Last 10 Proxy Access Logs ==="
if [ -f "/var/python/proxy-server/logs/access.log" ]; then
    tail -n 10 /var/python/proxy-server/logs/access.log
else
    echo "No proxy access logs found"
fi
echo

echo "=== Last 10 Proxy Error Logs ==="
if [ -f "/var/python/proxy-server/logs/error.log" ]; then
    tail -n 10 /var/python/proxy-server/logs/error.log
else
    echo "No proxy error logs found"
fi
echo

echo "=== System Resource Usage ==="
echo "CPU Usage:"
top -bn1 | head -3
echo
echo "Memory Usage:"
free -h
echo
echo "Disk Usage:"
df -h
