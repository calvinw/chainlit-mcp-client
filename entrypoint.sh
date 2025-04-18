#!/bin/bash
set -e

echo "🧹 Removing existing coffee_shop.db if it exists..."
rm -f coffee_shop.db

echo "⚙️ Rebuilding coffee_shop.db from coffee_shop.sql..."
sqlite3 coffee_shop.db < coffee_shop.sql

echo "🚀 Starting Chainlit app..."
exec uv run chainlit run app.py -h --host 0.0.0.0 --port 8080
