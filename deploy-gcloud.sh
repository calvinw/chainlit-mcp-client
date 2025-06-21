#!/bin/bash

# Google Cloud deployment script for Chainlit MCP Client

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load configuration if available
if [ -f "gcloud-config.env" ]; then
    echo -e "${BLUE}Loading configuration from gcloud-config.env...${NC}"
    source gcloud-config.env
fi

# Configuration (can be overridden by command line args)
PROJECT_ID=${1:-${PROJECT_ID:-"your-chainlit-mcp-project"}}
REGION=${2:-${REGION:-"us-central1"}}
SERVICE_NAME=${SERVICE_NAME:-"chainlit-mcp-client"}

echo -e "${YELLOW}Deploying Chainlit MCP Client to Google Cloud Run...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${YELLOW}Please login to gcloud first...${NC}"
    gcloud auth login
fi

# Set project
echo -e "${YELLOW}Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo -e "${YELLOW}Building and deploying with Cloud Build...${NC}"
gcloud builds submit --config cloudbuild.yaml

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo -e "${BLUE}Users will enter their OpenRouter API key through the chat interface.${NC}"