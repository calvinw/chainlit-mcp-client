#!/bin/bash
set -e

APP_NAME="chainlit-mcp-client"
PORT=8080

echo "🔨 Building Docker image: $APP_NAME..."
docker build -t $APP_NAME .

echo "🚀 Running Docker container and exposing port $PORT..."
docker run -p $PORT:$PORT $APP_NAME
