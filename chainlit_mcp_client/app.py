import json
import asyncio
import os
import logging

from mcp import ClientSession
import openai

import chainlit as cl
from chainlit.input_widget import Select, TextInput, Slider
from dotenv import load_dotenv

# Import from models.py and settings_manager.py
from models import OPENROUTER_MODELS, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from settings_manager import save_selected_model, load_selected_model

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SYSTEM = """You are a helpful assistant with some tools."""

@cl.action_callback("action_button")
async def on_action(action):
    await cl.Message(content=f"Executed {action.name}").send()
    # Optionally remove the action button from the chatbot user interface
    await action.remove()

@cl.on_chat_start
async def start():
    # Sending an action button within a chatbot message
    actions = [
        cl.Action(name="action_button", payload={"value": "example_value"}, label="Click me!")
    ]

    await cl.Message(content="Interact with this action button:", actions=actions).send()

def flatten(xss):
    return [x for xs in xss for x in xs]

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(label="List Your Tools", 
                   message="Can you list your available tools. Make sure to give the names and parameters and a description. Format it in a markdown table.")
    ]

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
    print(f"🔧 MCP DEBUG: Connecting to MCP server: {connection.name}")
    
    result = await session.list_tools()
    print(f"🔧 MCP DEBUG: MCP server '{connection.name}' returned {len(result.tools)} tools")
    
    # Store raw MCP tool definitions
    mcp_raw_tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
        } for t in result.tools]

    # Get existing data and ADD to it (don't replace)
    mcp_tools_data = cl.user_session.get("mcp_tools_data", {})
    mcp_tools_data[connection.name] = mcp_raw_tools
    cl.user_session.set("mcp_tools_data", mcp_tools_data)
    
    print(f"🔧 MCP DEBUG: Stored {len(mcp_raw_tools)} raw tools for '{connection.name}'")

    # Also store OpenAI formatted tools for easy access later
    openai_tools = [mcp_to_openai_tool(tool) for tool in mcp_raw_tools]
    mcp_openai_tools = cl.user_session.get("mcp_openai_tools", {})
    mcp_openai_tools[connection.name] = openai_tools
    cl.user_session.set("mcp_openai_tools", mcp_openai_tools)
    
    print(f"🔧 MCP DEBUG: Stored {len(openai_tools)} OpenAI tools for '{connection.name}'")
    print(f"🔧 MCP DEBUG: Total MCP connections now: {len(mcp_openai_tools)}")
    
    # List all connections and their tool counts
    for conn_name, conn_tools in mcp_openai_tools.items():
        print(f"🔧 MCP DEBUG: - Connection '{conn_name}': {len(conn_tools)} tools")

@cl.step(type="tool")
async def call_tool(tool_call):
    # Get tool name from the function call
    tool_name = tool_call.function.name
    
    # Add validation to handle empty or invalid arguments
    try:
        if not hasattr(tool_call.function, 'arguments') or not tool_call.function.arguments or tool_call.function.arguments.strip() == "":
            tool_input = {}  # Default to empty dict if no arguments
            # logger.info(f"Empty arguments for tool {tool_name}, using empty dict")
        else:
            tool_input = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        # Log the problematic value
        logger.error(f"Invalid JSON in arguments: '{tool_call.function.arguments}'")
        # For some tools, you might be able to infer the needed structure
        if tool_name == "query_sql":
            # Default structure for SQL queries - empty query will list tables
            tool_input = {"sql": ""}
        else:
            tool_input = {}  # Use empty dict as fallback

    current_step = cl.context.current_step
    current_step.name = tool_name
    current_step.input = tool_input  # Log the parsed input

    # Identify which mcp is used
    mcp_tools_data = cl.user_session.get("mcp_tools_data", {})  # Use raw data for lookup
    mcp_name = None

    for connection_name, tools in mcp_tools_data.items():
        if any(tool.get("name") == tool_name for tool in tools):
            mcp_name = connection_name
            break

    if not mcp_name:
        error_msg = json.dumps({"error": f"Tool {tool_name} not found in any MCP connection"})
        current_step.output = error_msg
        return {"tool_call_id": tool_call.id, "name": tool_name, "output": error_msg}

    # Get MCP session with better error handling
    session_tuple = cl.context.session.mcp_sessions.get(mcp_name)
    if not session_tuple:
        error_msg = json.dumps({"error": f"MCP session for {mcp_name} not found"})
        current_step.output = error_msg
        return {"tool_call_id": tool_call.id, "name": tool_name, "output": error_msg}

    mcp_session, _ = session_tuple

    try:
        # Call the tool with validated input
        tool_output = await mcp_session.call_tool(tool_name, tool_input)

        # Extract the content field which contains TextContent objects
        if hasattr(tool_output, 'content') and tool_output.content:
            # Find the TextContent object
            for item in tool_output.content:
                if hasattr(item, 'text'):
                    # This is what we want - just the table names text
                    result_text = item.text
                    break
            else:
                # If we didn't find a TextContent with text attribute
                result_text = "No tables found"
        else:
            # Fallback if content is not available
            result_text = "Unable to retrieve tables"
        
    except Exception as e:
        # Handle and log any exceptions during tool execution
        logger.error(f"Error calling tool {tool_name}: {str(e)}")
        error_msg = json.dumps({"error": str(e)})
        current_step.output = error_msg
        result_text = error_msg  # Send error back to OpenAI

    # Return format expected by OpenAI for tool results
    return {
        "tool_call_id": tool_call.id, 
        "name": tool_name, 
        "output": json.dumps(result_text)
    }

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
    
    # Debug MCP tools
    print(f"🔧 MCP DEBUG: Found {len(mcp_openai_tools)} MCP connections")
    print(f"🔧 MCP DEBUG: Total tools available: {len(tools)}")
    for conn_name, conn_tools in mcp_openai_tools.items():
        print(f"🔧 MCP DEBUG: Connection '{conn_name}' has {len(conn_tools)} tools")

    # Get settings
    settings = cl.user_session.get("settings", {})
    model = settings.get("Model")
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
        print(f"🔧 MCP DEBUG: Sending {len(tools)} tools to LLM")
    else:
        print("🔧 MCP DEBUG: NO TOOLS AVAILABLE - LLM won't see any tools!")

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
    # Load saved model (simple!)
    saved_model = await load_selected_model()
    print(f"🟦 PYTHON: Loaded model: {saved_model}")
    
    # Find the initial model index
    initial_model_index = 0
    if saved_model in OPENROUTER_MODELS:
        initial_model_index = OPENROUTER_MODELS.index(saved_model)
    
    # Create settings panel
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenRouter Model",
                values=OPENROUTER_MODELS,
                initial_index=initial_model_index,
            ),
            Slider(
                id="Temperature",
                label="Temperature",
                initial=DEFAULT_TEMPERATURE,
                min=0,
                max=2,
                step=0.1,
            )
        ]
    ).send()
    
    # Store settings in user session
    cl.user_session.set("settings", {
        "Model": saved_model,
        "Temperature": DEFAULT_TEMPERATURE
    })
    
    # Initialize chat messages only
    cl.user_session.set("chat_messages", [])
    
    # Preserve MCP data if it exists
    if not cl.user_session.get("mcp_tools_data"):
        cl.user_session.set("mcp_tools_data", {})
    if not cl.user_session.get("mcp_openai_tools"):
        cl.user_session.set("mcp_openai_tools", {})

# Settings update handler
@cl.on_settings_update
async def on_settings_update(settings):
    # Update settings in user session
    cl.user_session.set("settings", settings)
    
    # Save only the model selection to localStorage
    model = settings.get("Model")
    if model:
        await save_selected_model(model)
    
    # If API key was provided, store it in the env user session
    if "api_key" in settings:
        cl.user_session.set("env", {"OPENROUTER_API_KEY": settings["api_key"]})

# Chat end handler - save model when chat ends
@cl.on_chat_end
async def on_chat_end():
    """Save model when chat ends"""
    settings = cl.user_session.get("settings", {})
    model = settings.get("Model")
    if model:
        await save_selected_model(model)

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
