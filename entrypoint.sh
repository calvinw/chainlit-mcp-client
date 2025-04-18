#!/bin/bash
set -e

echo "🚀 Starting Chainlit app..."
exec uv run chainlit run app.py -h --host 0.0.0.0 --port 8080
