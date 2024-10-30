#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Testing Proxy Server ==="

# Test URLs
URLS=(
    "http://example.com"
    "https://example.com"
    "http://google.com"
    "https://google.com"
)

# Test proxy connection
echo "Testing proxy connection..."
if nc -zv localhost 8080 2>/dev/null; then
    echo -e "${GREEN}✓ Proxy is accessible${NC}"
else
    echo -e "${RED}✗ Cannot connect to proxy${NC}"
    exit 1
fi

# Test URLs
for url in "${URLS[@]}"; do
    echo -e "\nTesting: $url"
    if curl -s -o /dev/null -x localhost:8080 -w "%{http_code}" "$url" | grep -q "200"; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
done

# Test connection speed
echo -e "\nTesting connection speed..."
time curl -s -x localhost:8080 http://example.com > /dev/null

echo -e "\nTest complete!"