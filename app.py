import json
import asyncio
import os
import sqlite3
import logging

from mcp import ClientSession
import openai  # Changed import

import chainlit as cl
from chainlit.input_widget import Select, TextInput
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize and create database from SQL file
def initialize_database():
    db_path = "coffee_shop.db"
    sql_path = "coffee_shop.sql"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        logger.info(f"Removing existing database: {db_path}")
        os.remove(db_path)
    
    # Create a new database
    logger.info(f"Creating new database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    try:
        # Read SQL file
        with open(sql_path, 'r') as sql_file:
            sql_script = sql_file.read()
        
        # Execute SQL script
        conn.executescript(sql_script)
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

# Run database initialization before anything else
initialize_database()

load_dotenv()

# Configure project settings in config.toml to require API key
def modify_config_file():
    """Add the required API key to the config file if not already there"""
    import toml
    import os
    
    config_path = os.path.join('.chainlit', 'config.toml')
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Read existing config if it exists
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
        except Exception as e:
            logger.error(f"Error reading config file: {str(e)}")
    
    # Ensure project section exists
    if 'project' not in config:
        config['project'] = {}
    
    # Add OpenRouter API key to required user env variables
    if 'user_env' not in config['project']:
        config['project']['user_env'] = ["OPENROUTER_API_KEY"]
    elif "OPENROUTER_API_KEY" not in config['project']['user_env']:
        config['project']['user_env'].append("OPENROUTER_API_KEY")
    
    # Write back the config
    try:
        with open(config_path, 'w') as f:
            toml.dump(config, f)
        logger.info("Updated config file to require API key")
    except Exception as e:
        logger.error(f"Error writing config file: {str(e)}")

# Call the function to modify config
modify_config_file()

# Define available models globally using the user's list
AVAILABLE_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "google/gemini-2.0-flash-001",
    "google/gemini-2.0-flash-lite-001",
    "google/gemini-flash-1.5",
    "google/gemini-flash-1.5-8b",
    "anthropic/claude-3-haiku"
]

SYSTEM = "you are a helpful assistant."

def flatten(xss):
    return [x for xs in xss for x in xs]

# Convert MCP tool schema to OpenAI tool schema
def mcp_to_openai_tool(mcp_tool):
    return {
        "type": "function",
        "function": {
            "name": mcp_tool["name"],
            "description": mcp_tool["description"],
            "parameters": mcp_tool["input_schema"],
        }
    }

@cl.on_mcp_connect
async def on_mcp(connection, session: ClientSession):
    result = await session.list_tools()
    # Store raw MCP tool definitions
    mcp_raw_tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
        } for t in result.tools]

    mcp_tools_data = cl.user_session.get("mcp_tools_data", {})
    mcp_tools_data[connection.name] = mcp_raw_tools
    cl.user_session.set("mcp_tools_data", mcp_tools_data)

    # Also store OpenAI formatted tools for easy access later
    openai_tools = [mcp_to_openai_tool(tool) for tool in mcp_raw_tools]
    mcp_openai_tools = cl.user_session.get("mcp_openai_tools", {})
    mcp_openai_tools[connection.name] = openai_tools
    cl.user_session.set("mcp_openai_tools", mcp_openai_tools)

@cl.step(type="tool")
async def call_tool(tool_call): # Parameter changed slightly for clarity
    tool_name = tool_call.function.name
    tool_input = json.loads(tool_call.function.arguments) # OpenAI sends arguments as JSON string

    current_step = cl.context.current_step
    current_step.name = tool_name
    current_step.input = tool_input # Log the parsed input

    # Identify which mcp is used
    mcp_tools_data = cl.user_session.get("mcp_tools_data", {}) # Use raw data for lookup
    mcp_name = None

    for connection_name, tools in mcp_tools_data.items():
        if any(tool.get("name") == tool_name for tool in tools):
            mcp_name = connection_name
            break

    if not mcp_name:
        error_msg = json.dumps({"error": f"Tool {tool_name} not found in any MCP connection"})
        current_step.output = error_msg
        return {"tool_call_id": tool_call.id, "name": tool_name, "output": error_msg} # Return format for OpenAI

    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)

    if not mcp_session:
        error_msg = json.dumps({"error": f"MCP {mcp_name} session not found"})
        current_step.output = error_msg
        return {"tool_call_id": tool_call.id, "name": tool_name, "output": error_msg} # Return format for OpenAI

    try:
        tool_output = await mcp_session.call_tool(tool_name, tool_input)
        current_step.output = tool_output # Log the actual output
    except Exception as e:
        error_msg = json.dumps({"error": str(e)})
        current_step.output = error_msg
        tool_output = error_msg # Send error back to OpenAI

    # Return format expected by OpenAI for tool results
    return {"tool_call_id": tool_call.id, "name": tool_name, "output": json.dumps(str(tool_output))} # Convert tool_output to string

async def get_openai_client(api_key):
    """Creates a new OpenAI client with the given API key."""
    if not api_key:
        raise ValueError("API Key is required to make requests")
    
    return openai.AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

async def call_llm(chat_messages, api_key):
    msg = cl.Message(content="")
    mcp_openai_tools = cl.user_session.get("mcp_openai_tools", {})
    # Flatten the OpenAI-formatted tools from all MCP connections
    tools = flatten([tools for _, tools in mcp_openai_tools.items()])

    # Prepare arguments for OpenAI API call
    api_args = {
        "model": cl.user_session.get("selected_model"),
        "messages": [{"role": "system", "content": SYSTEM}] + chat_messages,
        "temperature": 0,
        "stream": True,
    }
    if tools:
        api_args["tools"] = tools
        api_args["tool_choice"] = "auto"

    # Make the API call with the provided API key for this request
    client = await get_openai_client(api_key)
    stream_resp = await client.chat.completions.create(**api_args)

    # Stream the response
    full_response = ""
    tool_calls = []
    async for chunk in stream_resp:
        delta = chunk.choices[0].delta
        if delta.content:
            full_response += delta.content
            await msg.stream_token(delta.content)
        if delta.tool_calls:
            # Append tool call chunks to reconstruct the full tool call later
            for tool_call_chunk in delta.tool_calls:
                 # Initialize tool_calls entry if index doesn't exist
                if tool_call_chunk.index >= len(tool_calls):
                    tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})

                # Update the specific tool call entry
                tc = tool_calls[tool_call_chunk.index]
                if tool_call_chunk.id:
                    tc["id"] = tool_call_chunk.id
                if tool_call_chunk.function:
                    if tool_call_chunk.function.name:
                        tc["function"]["name"] = tool_call_chunk.function.name
                    if tool_call_chunk.function.arguments:
                        tc["function"]["arguments"] += tool_call_chunk.function.arguments

    await msg.update()

    # Construct the final assistant message object for history
    assistant_message = {"role": "assistant", "content": full_response}
    if tool_calls:
        assistant_message["tool_calls"] = tool_calls

    return assistant_message

@cl.on_chat_start
async def start_chat():
    # Prepare model options for the dropdown
    model_values = [model.split('/')[-1] for model in AVAILABLE_MODELS]
    
    # Create settings panel with ONLY model selector (no API key here)
    settings = await cl.ChatSettings(
        [
            Select(
                id="model_selector",
                label="Select Model",
                values=model_values,
                initial_index=0
            )
        ]
    ).send()
    
    # Extract model value from settings
    selected_model_name = settings["model_selector"]
    
    # Find full model path from the selected name
    for model in AVAILABLE_MODELS:
        if model.split('/')[-1] == selected_model_name:
            selected_model = model
            break
    else:
        selected_model = AVAILABLE_MODELS[0]  # Default if not found
    
    # Set session variables for the model and message history
    cl.user_session.set("selected_model", selected_model)
    cl.user_session.set("chat_messages", [])
    cl.user_session.set("mcp_tools_data", {})
    cl.user_session.set("mcp_openai_tools", {})
    
    # Welcome message
    await cl.Message(content=f"Welcome! Please provide your OpenRouter API Key in the API Keys section (key icon in the top right) before starting. Current model selected: **{selected_model}**").send()

# Settings update handler
@cl.on_settings_update
async def on_settings_update(settings):
    # Extract model value from settings
    selected_model_name = settings["model_selector"]
    
    # Find full model path from the selected name
    for model in AVAILABLE_MODELS:
        if model.split('/')[-1] == selected_model_name:
            selected_model = model
            break
    else:
        selected_model = AVAILABLE_MODELS[0]  # Default if not found
    
    # Update only the model in session variables
    cl.user_session.set("selected_model", selected_model)
    
    # Confirm model update
    await cl.Message(content=f"Settings updated. Now using model: **{selected_model}**").send()

@cl.on_message
async def on_message(msg: cl.Message):
    # Get the API key from environment variables section
    api_keys = cl.user_session.get("_api_keys", {})
    api_key = api_keys.get("OPENROUTER_API_KEY", "")
    
    # Validate API key
    if not api_key:
        await cl.ErrorMessage(content="Please provide your OpenRouter API Key in the API Keys section (key icon in the top right) before continuing.").send()
        return
    
    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "user", "content": msg.content})

    if not chat_messages or chat_messages[0].get("role") != "system":
         chat_messages.insert(0, {"role": "system", "content": SYSTEM})

    while True:
        messages_for_api = [msg for msg in chat_messages if msg.get("role") != "system"]
        assistant_message = await call_llm(messages_for_api, api_key)
        chat_messages.append(assistant_message)

        if not assistant_message.get("tool_calls"):
            break

        tool_tasks = []
        for tool_call_dict in assistant_message["tool_calls"]:
            class ToolCall:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
                    if 'function' in kwargs and isinstance(kwargs['function'], dict):
                        self.function = type('Function', (), kwargs['function'])()

            tool_call_obj = ToolCall(**tool_call_dict)
            tool_tasks.append(call_tool(tool_call_obj))

        tool_results = await asyncio.gather(*tool_tasks)

        for result in tool_results:
             chat_messages.append({
                 "role": "tool",
                 "tool_call_id": result["tool_call_id"],
                 "name": result["name"],
                 "content": result["output"],
             })

    cl.user_session.set("chat_messages", chat_messages)
