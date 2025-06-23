#!/bin/bash
set -e

APP_NAME="chainlit-mcp-client"
COOLIFY_HOST="your-droplet-ip"  # Replace with your droplet IP
COOLIFY_TOKEN="your-api-token"  # Replace with your Coolify API token
PROJECT_ID="your-project-id"    # Replace with your Coolify project ID

echo "🚀 Deploying $APP_NAME to Coolify..."

# Trigger deployment via Coolify API
curl -X POST \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  "http://$COOLIFY_HOST:8000/api/v1/projects/$PROJECT_ID/applications/$APP_NAME/deploy"

echo "✅ Deployment triggered successfully!"
echo "🌐 Check your Coolify dashboard for deployment status"