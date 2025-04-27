#!/bin/bash
set -e

PORT=${PORT:-8080}  # Default to 8080 if not set (for local dev)
echo "🚀 Starting Chainlit app on port $PORT..."
exec uv run chainlit run app.py --host 0.0.0.0 --port "$PORT"
