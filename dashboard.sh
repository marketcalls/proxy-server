#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
check_service() {
    if systemctl is-active --quiet proxy-server; then
        echo -e "${GREEN}Proxy Server Status: Running${NC}"
    else
        echo -e "${RED}Proxy Server Status: Not Running${NC}"
    fi
}

check_resources() {
    echo -e "\n${YELLOW}System Resources:${NC}"
    echo "CPU Usage:"
    top -bn1 | head -3
    echo -e "\nMemory Usage:"
    free -h
    echo -e "\nDisk Usage:"
    df -h /
}

check_connections() {
    echo -e "\n${YELLOW}Current Connections:${NC}"
    echo "Total connections: $(netstat -ant | grep :8080 | wc -l)"
    echo -e "\nConnection states:"
    netstat -ant | grep :8080 | awk '{print $6}' | sort | uniq -c
}

check_logs() {
    echo -e "\n${YELLOW}Recent Errors (last hour):${NC}"
    grep "ERROR" /var/python/proxy-server/logs/error.log | tail -n 5

    echo -e "\n${YELLOW}Recent Access (last 10):${NC}"
    tail -n 10 /var/python/proxy-server/logs/access.log
}

check_security() {
    echo -e "\n${YELLOW}Security Status:${NC}"
    echo "UFW Status:"
    sudo ufw status | head -n 5
    
    echo -e "\nFail2ban Status:"
    sudo fail2ban-client status | head -n 5
}

# Main Dashboard
clear
echo "======================================"
echo "     Proxy Server Monitor Dashboard    "
echo "======================================"
date
echo "--------------------------------------"

check_service
check_resources
check_connections
check_logs
check_security

echo -e "\n======================================"