#!/bin/bash

echo "Starting ThakaaMed Dental Integration Services..."

# Check PostgreSQL
echo "Checking PostgreSQL..."
if ! pg_isready -h localhost -p 5432; then
    echo "Starting PostgreSQL..."
    brew services start postgresql@14
fi

# Start SAIF API
echo "Starting SAIF API Gateway..."
cd api-gateway
nohup python saif_api.py > saif_api.log 2>&1 &
echo $! > saif_api.pid

# Check Mirth Connect
echo "Checking Mirth Connect..."
if ! curl -s http://localhost:8080 > /dev/null; then
    echo "Please start Mirth Connect manually"
else
    echo "Mirth Connect is running"
fi

echo "All services started!"