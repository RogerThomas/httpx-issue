#!/bin/bash

# Load test the services endpoint with hey
# Default: 1000 requests with 10 concurrent clients
# Usage: ./hey.sh [requests] [concurrent] [verbose]

# Set default values and allow overrides from command line arguments
REQUESTS=${1:-10000}
CONCURRENT=${2:-200}
CLIENT=${3:-httpx}

echo "Running load test with $REQUESTS requests and $CONCURRENT concurrent clients"

echo "Command: hey -n $REQUESTS -c $CONCURRENT http://localhost:8000/main?http_client=$CLIENT"

hey -n $REQUESTS -c $CONCURRENT http://localhost:8000/main?http_client=$CLIENT
