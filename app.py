import json
import asyncio
import os
import logging

from mcp import ClientSession
import openai

import chainlit as cl
from chainlit.input_widget import Select, TextInput, Slider
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SYSTEM = "You are a helpful assistant. If you query the database for records, always put the records as a markdown table."

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

    # Get settings
    settings = cl.user_session.get("settings", {})
    model = settings.get("Model", "google/gemini-2.0-flash-001")
    temperature = float(settings.get("Temperature", 0))

    # Prepare arguments for OpenAI API call
    api_args = {
        "model": model,
        "messages": [
                     {
                      "role": "system", 
                      "content": SYSTEM
                      }
                     ] + chat_messages,
        "temperature": temperature,
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
    # Create settings panel with model selector, temperature slider, and API key input
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenRouter Model",
                values=[
                    "google/gemini-2.0-flash-001",
                    "google/gemini-2.0-flash-lite-001",
                    "google/gemini-flash-1.5",
                    "google/gemini-flash-1.5-8b",
                    "openai/gpt-4o-mini",
                    "openai/gpt-4o",
                    "anthropic/claude-3-haiku"
                ],
                initial_index=0,
            ),
            Slider(
                id="Temperature",
                label="Temperature",
                initial=0,
                min=0,
                max=2,
                step=0.1,
            )
        ]
    ).send()
    
    # Store initial settings values in user session
    initial_settings = {
        "Model": "google/gemini-2.0-flash-001",
        "Temperature": 0                
    }
    cl.user_session.set("settings", initial_settings)
    
    # Set session variables for message history and tools
    cl.user_session.set("chat_messages", [])
    cl.user_session.set("mcp_tools_data", {})
    cl.user_session.set("mcp_openai_tools", {})

# Settings update handler
@cl.on_settings_update
async def on_settings_update(settings):
    # Update all settings in user session
    cl.user_session.set("settings", settings)
    
    # If API key was provided, store it in the env user session
    if "api_key" in settings:
        cl.user_session.set("env", {"OPENROUTER_API_KEY": settings["api_key"]})
    
    # Get the current model setting
    model = settings.get("Model", "google/gemini-2.0-flash-001")
    
@cl.on_message
async def on_message(msg: cl.Message):
    # Get API key from environment variables in user session
    user_env = cl.user_session.get("env", {})
    api_key = user_env.get("OPENROUTER_API_KEY")
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
