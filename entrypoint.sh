#!/bin/bash
set -e

PORT=${PORT:-8080}
echo "🚀 Starting Chainlit app on port $PORT..."

# Set the app root to the container path
export CHAINLIT_APP_ROOT=/app/chainlit_mcp_client

# Ensure the .files directory exists
mkdir -p "$CHAINLIT_APP_ROOT/.files"

# Run the chainlit app
exec uv run chainlit run chainlit_mcp_client/app.py --host 0.0.0.0 --port "$PORT"
