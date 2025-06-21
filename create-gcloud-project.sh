#!/bin/bash

# Script to create a new Google Cloud project for Chainlit MCP Client

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default project configuration
DEFAULT_PROJECT_ID="chainlit-mcp-client-$(date +%Y%m%d)"
DEFAULT_PROJECT_NAME="Chainlit MCP Client"
DEFAULT_REGION="us-central1"

echo -e "${BLUE}🚀 Google Cloud Project Setup for Chainlit MCP Client${NC}"
echo "=================================================="

# Get project ID from user or use default
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter project ID (or press Enter for default: ${DEFAULT_PROJECT_ID}):${NC}"
    read -r PROJECT_ID
    PROJECT_ID=${PROJECT_ID:-$DEFAULT_PROJECT_ID}
else
    PROJECT_ID=$1
fi

# Get project name
if [ -z "$2" ]; then
    PROJECT_NAME="$DEFAULT_PROJECT_NAME"
else
    PROJECT_NAME="$2"
fi

echo -e "${YELLOW}Creating project: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Project name: ${PROJECT_NAME}${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${YELLOW}Please login to gcloud first...${NC}"
    gcloud auth login
fi

# Create the project
echo -e "${YELLOW}Creating Google Cloud project...${NC}"
gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME"

# Set the project as active
echo -e "${YELLOW}Setting project as active...${NC}"
gcloud config set project "$PROJECT_ID"

# Enable billing (user will need to do this manually in console)
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create a config file for this project
cat > gcloud-config.env << EOF
# Google Cloud configuration for Chainlit MCP Client
PROJECT_ID=$PROJECT_ID
PROJECT_NAME=$PROJECT_NAME
REGION=$DEFAULT_REGION
SERVICE_NAME=chainlit-mcp-client
EOF

echo -e "${GREEN}✅ Project created successfully!${NC}"
echo -e "${GREEN}Project ID: ${PROJECT_ID}${NC}"
echo -e "${GREEN}Configuration saved to: gcloud-config.env${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: You need to enable billing for this project${NC}"
echo -e "${YELLOW}   Visit: https://console.cloud.google.com/billing/linkedaccount?project=${PROJECT_ID}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Enable billing in the Google Cloud Console"
echo "2. Run: ./deploy-gcloud.sh $PROJECT_ID"
echo "3. Share the deployed URL - users will enter their own OpenRouter API key"