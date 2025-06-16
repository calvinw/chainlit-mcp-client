# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chainlit-based MCP (Model Context Protocol) client that allows users to connect to various MCP servers and interact with them through a chat interface. The application serves as a bridge between users and remote MCP servers, providing tools for database queries, data analysis, and other MCP-enabled services.

## Architecture

- **Frontend**: Chainlit web interface with chat functionality and settings panel
- **Backend**: Python application using the MCP library for server connections
- **LLM Integration**: OpenRouter API for accessing various language models (Anthropic, OpenAI, Google, etc.)
- **Tool System**: Dynamic tool loading from connected MCP servers, converted to OpenAI tool format
- **User Persistence**: Settings automatically saved and restored using hashed API key as user identifier

Key components:
- `chainlit_mcp_client/app.py` - Main application with MCP connection handling, chat logic, model definitions, and user settings persistence
- `chainlit_mcp_client/app-sqlite3.py` - Alternative version with SQLite integration (if exists)

## Development Commands

### Running the Application
```bash
# Local development (standard version)
./run-local.sh

# Local development (SQLite version)  
./run-sqlite.sh

# Docker deployment
./run-docker.sh
```

### Package Management
```bash
# Install dependencies
uv install

# Run with uv (used by scripts)
uv run chainlit run chainlit_mcp_client/app.py --host 0.0.0.0 --port 8080
```

## User Settings Persistence

The application automatically saves and restores user preferences:
- **User ID**: Generated from hashed OpenRouter API key for privacy
- **Storage**: JSON files in `user_settings/` directory 
- **Data**: Model selection and temperature preferences
- **Experience**: Automatic restoration on return visits with welcome message

## MCP Integration

The application dynamically connects to MCP servers and exposes their tools through the chat interface. MCP tools are automatically converted from MCP format to OpenAI function calling format.

Key MCP handling:
- `@cl.on_mcp_connect` decorator handles new MCP connections
- Tools are stored in user session under `mcp_tools_data` (raw) and `mcp_openai_tools` (formatted)
- Tool calls route through `call_tool()` function which identifies the correct MCP session

## Environment Variables

- `OPENROUTER_API_KEY` - Required for LLM access (can be set via chat interface)
- `PORT` - Application port (default: 8080)
- `CHAINLIT_APP_ROOT` - Set by run scripts to current directory structure

## Database Examples

The README contains extensive examples of Dolt databases that can be queried through connected MCP servers, including business management benchmarks, retail orders, engagement marketing, and the Sakila DVD rental database.