#!/bin/bash
set -e

PORT=8081
echo "🚀 Starting Chainlit MCP Remote Client on port $PORT..."

# Set the app root to the current directory structure
export CHAINLIT_APP_ROOT=$(pwd)/chainlit_mcp_client

# Ensure the .files directory exists
mkdir -p "$CHAINLIT_APP_ROOT/.files"

# Run the chainlit app on port 8081 for remote MCP servers
exec uv run chainlit run chainlit_mcp_client/app.py --host 0.0.0.0 --port "$PORT"