#!/bin/bash
# Get current WSL2 IP address and update frontend .env.local

WSL_IP=$(hostname -I | awk '{print $1}')

echo "Current WSL2 IP: $WSL_IP"

# Update frontend .env.local
sed -i "s|NEXT_PUBLIC_BACKEND_API_URL=http://.*:8000|NEXT_PUBLIC_BACKEND_API_URL=http://$WSL_IP:8000|" frontend/.env.local

echo "✅ Updated frontend/.env.local with WSL2 IP: $WSL_IP"
echo ""
echo "To use localhost instead, run in Windows PowerShell as Admin:"
echo "netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$WSL_IP"
