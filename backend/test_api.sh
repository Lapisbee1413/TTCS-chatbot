#!/bin/bash
echo "Testing Backend API Endpoints..."
echo ""

BASE_URL="http://localhost:8000"

echo "1. Health Check"
curl -s $BASE_URL/health | python -m json.tool
echo -e "\n"

echo "2. Root Endpoint"
curl -s $BASE_URL/ | python -m json.tool
echo -e "\n"

echo "3. List Documents"
curl -s $BASE_URL/api/documents | python -m json.tool
echo -e "\n"

echo "✓ Basic tests completed!"
echo "For full tests, start the server and run this script"
