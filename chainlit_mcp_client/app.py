import json
import asyncio
import os
import logging
import hashlib
from datetime import datetime

from mcp import ClientSession
import openai

import chainlit as cl
from chainlit.input_widget import Select, TextInput, Slider, Switch
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SYSTEM = """You are a helpful assistant with some tools."""

# Available OpenRouter models
OPENROUTER_MODELS = [
    # Google Models
    "google/gemini-2.5-flash-preview-05-20",
    "google/gemini-2.5-flash-preview",
    "google/gemini-2.5-flash-preview:thinking",
    "google/gemini-2.5-pro-preview-05-06",
    "google/gemini-2.5-pro-preview",
    "google/gemini-2.5-flash-preview-05-20:thinking",
    "google/gemini-pro-1.5",
    "google/gemini-flash-1.5",
    "google/gemini-flash-1.5-8b",
    
    # Anthropic Models
    "anthropic/claude-opus-4",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-3.5-haiku",
    "anthropic/claude-3.5-haiku-20241022",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-3-haiku",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-sonnet",
    
    # OpenAI Models
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/o4-mini-high",
    "openai/o4-mini",
    "openai/o3",
    "openai/o1-mini",
    "openai/o1-preview",
    "openai/gpt-4.1",
    "openai/gpt-4.1-nano",
    "openai/gpt-4.1-mini",
    "openai/gpt-3.5-turbo",
    "openai/codex-mini",
    
    # Qwen Models
    "qwen/qwen3-30b-a3b",
    "qwen/qwen3-14b",
    "qwen/qwen3-32b",
    "qwen/qwen3-235b-a22b",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "qwen/qwen-2.5-coder-32b-instruct",
    
    # DeepSeek Models
    "deepseek/deepseek-chat:free",
    "deepseek/deepseek-chat",
    
    # Mistral Models
    "mistralai/mistral-large",
    "mistralai/mistral-small",
    "mistralai/mistral-tiny",
    "mistralai/mistral-medium"
]

# Default model selection
DEFAULT_MODEL = "google/gemini-2.5-flash-preview-05-20"
DEFAULT_TEMPERATURE = 0

# User settings persistence
USER_SETTINGS_DIR = "user_settings"

def get_user_id_from_api_key(api_key):
    """Create a consistent user ID from API key"""
    if not api_key:
        return None
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]

def get_user_settings_path(user_id):
    """Get the file path for user settings"""
    os.makedirs(USER_SETTINGS_DIR, exist_ok=True)
    return os.path.join(USER_SETTINGS_DIR, f"{user_id}.json")

def save_user_settings(user_id, settings):
    """Save user's preferred settings"""
    if not user_id:
        return
    path = get_user_settings_path(user_id)
    settings_with_timestamp = {
        **settings,
        "last_updated": datetime.now().isoformat()
    }
    with open(path, 'w') as f:
        json.dump(settings_with_timestamp, f, indent=2)
    logger.info(f"Saved settings for user {user_id}: {settings}")

def load_user_settings(user_id):
    """Load user's saved settings, return None if none exist"""
    if not user_id:
        return None
    path = get_user_settings_path(user_id)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                settings = json.load(f)
            logger.info(f"Loaded settings for user {user_id}: {settings}")
            return settings
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading settings for user {user_id}: {e}")
    return None

import chainlit as cl

@cl.action_callback("action_button")
async def action_button_callback(action):
    await handle_action(action)


@cl.action_callback("list_tools")
async def list_tools_callback(action):
    """Send the list tools prompt to the LLM"""
    # Create a fake message with the starter prompt
    starter_message = "Can you list your available tools. Make sure to give the names and parameters and a description. Format it in table."
    
    class FakeMessage:
        def __init__(self, content):
            self.content = content
    
    fake_msg = FakeMessage(starter_message)
    await on_message(fake_msg)

    


async def handle_action(action):
    """Handle all action button clicks"""
    if action.name == "action_button":
        await cl.Message(content=f"Executed {action.name}").send()
        return
    
    # Handle tool-specific action button clicks
    if action.name.startswith("tool_"):
        payload = action.payload
        tool_name = payload.get("tool_name")
        params = payload.get("params", {})
        connection_name = payload.get("connection")
        
        # Format parameters as function call
        if params:
            # Format values properly (strings in quotes, others as-is)
            formatted_params = []
            for k, v in params.items():
                if isinstance(v, str):
                    formatted_params.append(f'"{v}"')
                else:
                    formatted_params.append(str(v))
            params_str = ",".join(formatted_params)
        else:
            params_str = ""
        
        # Create a message that looks like a function call
        message_content = f"Call {tool_name}({params_str})"
        
        # Show the function call and process it
        await cl.Message(content=f"⚡ {message_content}").send()
        
        # Create a fake message object and trigger the message handler
        class FakeMessage:
            def __init__(self, content):
                self.content = content
        
        fake_msg = FakeMessage(message_content)
        await on_message(fake_msg)

@cl.on_chat_start
async def start():
    # Sending an action button within a chatbot message
    actions = [
        cl.Action(name="action_button", payload={"value": "example_value"}, label="Click me!")
    ]

    await cl.Message(content="Interact with this action button:", actions=actions).send()

def flatten(xss):
    return [x for xs in xss for x in xs]

def generate_sample_params(input_schema, tool_name=None):
    """Generate parameters using only defaults from schema. Returns None if any required parameter lacks a default."""
    if not input_schema or not isinstance(input_schema, dict):
        return {}
    
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    sample_params = {}
    
    # First check if all required parameters have defaults
    for param_name in required:
        if param_name not in properties:
            return None  # Required parameter not defined in properties
        param_info = properties[param_name]
        if "default" not in param_info:
            return None  # Required parameter lacks default value
    
    # If we get here, all required parameters have defaults
    for param_name, param_info in properties.items():
        # Only use parameters that have explicit defaults
        if "default" in param_info:
            sample_params[param_name] = param_info["default"]
    
    return sample_params

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(label="List Your Tools", 
                   message="Can you list your available tools. Make sure to give the names and parameters and a description. Format it in table.")
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

    # Check if user wants default tool call buttons
    settings = cl.user_session.get("settings", {})
    create_tool_buttons = settings.get("CreateToolButtons", False)
    
    if create_tool_buttons:
        # Create action buttons for each tool with sample parameters
        actions = []
        for tool in mcp_raw_tools:
            # Generate sample parameters based on the tool's input schema
            sample_params = generate_sample_params(tool.get("input_schema", {}), tool["name"])
            
            # Skip this tool if it doesn't have complete defaults
            if sample_params is None:
                continue
            
            action_name = f"tool_{tool['name']}"
            
            # Register callback for this specific tool action
            @cl.action_callback(action_name)
            async def tool_action_callback(action):
                await handle_action(action)
            
            # Format parameters for button label
            if sample_params:
                # Format values properly (strings in quotes, others as-is)
                formatted_params = []
                for k, v in sample_params.items():
                    if isinstance(v, str):
                        formatted_params.append(f'"{v}"')
                    else:
                        formatted_params.append(str(v))
                params_display = ",".join(formatted_params)
                button_label = f"🛠️ {tool['name']}({params_display})"
            else:
                button_label = f"🛠️ {tool['name']}()"
            
            actions.append(
                cl.Action(
                    name=action_name, 
                    payload={
                        "tool_name": tool["name"],
                        "params": sample_params,
                        "connection": connection.name
                    }, 
                    label=button_label
                )
            )
        
        if actions:
            # Create control buttons that go first
            control_actions = []
            
            # Add list tools button first
            list_tools_action = cl.Action(
                name="list_tools",
                payload={},
                label="📊 List Tools"
            )
            control_actions.append(list_tools_action)
            
            
            
            # Combine control buttons first, then tool buttons
            all_actions = control_actions + actions
            
            # Send connection message with action buttons
            await cl.Message(
                content=f"🌐 Connected to {connection.name} with {len(actions)} tools",
                actions=all_actions
            ).send()

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
    
    # Check if user has API key from localStorage and can restore preferences
    user_env = cl.user_session.get("env", {})
    api_key = user_env.get("OPENROUTER_API_KEY")
    
    # Default settings
    initial_model_index = 0
    initial_temp = DEFAULT_TEMPERATURE
    initial_tool_buttons = False  # Default to off
    
    # If API key available from localStorage, try to restore user preferences
    if api_key:
        user_id = get_user_id_from_api_key(api_key)
        saved_settings = load_user_settings(user_id)
        
        if saved_settings:
            # Find index of their preferred model
            preferred_model = saved_settings.get("Model", DEFAULT_MODEL)
            if preferred_model in OPENROUTER_MODELS:
                initial_model_index = OPENROUTER_MODELS.index(preferred_model)
            initial_temp = saved_settings.get("Temperature", DEFAULT_TEMPERATURE)
            initial_tool_buttons = saved_settings.get("CreateToolButtons", False)
    
    # Create settings panel with restored or default values
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
                initial=initial_temp,
                min=0,
                max=2,
                step=0.1,
            ),
            Switch(
                id="CreateToolButtons",
                label="Create Default Tool Calls",
                initial=initial_tool_buttons,
            )
        ]
    ).send()
    
    # Store initial settings values in user session
    initial_settings = {
        "Model": OPENROUTER_MODELS[initial_model_index],
        "Temperature": initial_temp,
        "CreateToolButtons": initial_tool_buttons               
    }
    cl.user_session.set("settings", initial_settings)
    
    # Set session variables for message history and tools
    cl.user_session.set("chat_messages", [])
    cl.user_session.set("mcp_tools_data", {})
    cl.user_session.set("mcp_openai_tools", {})

# Settings update handler
@cl.on_settings_update
async def on_settings_update(settings):
    # Get previous settings to check for model changes
    previous_settings = cl.user_session.get("settings", {})
    previous_model = previous_settings.get("Model")
    new_model = settings.get("Model")
    
    # Update all settings in user session
    cl.user_session.set("settings", settings)
    
    # If model changed and we have chat messages (not a new chat), show model selection message
    chat_messages = cl.user_session.get("chat_messages", [])
    if previous_model and new_model and previous_model != new_model and len(chat_messages) > 0:
        await cl.Message(f"Switched to {new_model}").send()
    
    # If API key was provided, store it in the env user session
    if "api_key" in settings:
        api_key = settings["api_key"]
        cl.user_session.set("env", {"OPENROUTER_API_KEY": api_key})
        
        # Also save user preferences for future sessions
        user_id = get_user_id_from_api_key(api_key)
        if user_id:
            user_prefs = {
                "Model": settings.get("Model"),
                "Temperature": settings.get("Temperature"),
                "CreateToolButtons": settings.get("CreateToolButtons")
            }
            save_user_settings(user_id, user_prefs)
    else:
        # Even without API key change, save preferences if we have an existing API key
        user_env = cl.user_session.get("env", {})
        api_key = user_env.get("OPENROUTER_API_KEY")
        if api_key:
            user_id = get_user_id_from_api_key(api_key)
            if user_id:
                user_prefs = {
                    "Model": settings.get("Model"),
                    "Temperature": settings.get("Temperature"),
                    "CreateToolButtons": settings.get("CreateToolButtons")
                }
                save_user_settings(user_id, user_prefs)
    
@cl.on_message
async def on_message(msg: cl.Message):
    # Get API key from environment variables in user session
    user_env = cl.user_session.get("env", {})
    api_key = user_env.get("OPENROUTER_API_KEY")
    chat_messages = cl.user_session.get("chat_messages", [])
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
