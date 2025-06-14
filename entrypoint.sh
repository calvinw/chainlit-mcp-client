#!/bin/bash
set -e

PORT=${PORT:-8080}
echo "🚀 Starting Chainlit app on port $PORT..."
exec uv run chainlit run chainlit_mcp_client/app.py --host 0.0.0.0 --port "$PORT"
