import json
import asyncio
import os

from mcp import ClientSession
import openai  # Changed import

import chainlit as cl
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI() # Changed client initialization
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


async def call_openai(chat_messages): # Renamed function
    msg = cl.Message(content="")
    mcp_openai_tools = cl.user_session.get("mcp_openai_tools", {})
    # Flatten the OpenAI-formatted tools from all MCP connections
    tools = flatten([tools for _, tools in mcp_openai_tools.items()])

    # Prepare arguments for OpenAI API call
    api_args = {
        "model": "gpt-4o-mini", # Or another suitable OpenAI model
        "messages": [{"role": "system", "content": SYSTEM}] + chat_messages,
        "temperature": 0,
        "stream": True,
    }
    if tools:
        api_args["tools"] = tools
        api_args["tool_choice"] = "auto"

    # Make the API call
    stream_resp = await openai_client.chat.completions.create(**api_args)

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


    await msg.update() # Ensure the complete message is displayed

    # Construct the final assistant message object for history
    assistant_message = {"role": "assistant", "content": full_response}
    if tool_calls:
         # Convert reconstructed tool calls list to OpenAI's ToolCall objects for consistency if needed later
         # For history, the dictionary format is sufficient
        assistant_message["tool_calls"] = tool_calls


    return assistant_message # Return the full message object including potential tool calls


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("chat_messages", [])
    cl.user_session.set("mcp_tools_data", {}) # Initialize storage for raw MCP tool data
    cl.user_session.set("mcp_openai_tools", {}) # Initialize storage for OpenAI formatted tools


@cl.on_message
async def on_message(msg: cl.Message):
    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "user", "content": msg.content})

    while True: # Loop to handle potential multiple tool calls
        assistant_message = await call_openai(chat_messages)
        chat_messages.append(assistant_message) # Add assistant's response (text + tool_calls)

        if not assistant_message.get("tool_calls"):
            break # Exit loop if no tool calls

        # Prepare tasks for concurrent execution
        tool_tasks = []
        for tool_call_dict in assistant_message["tool_calls"]:
            # Create a simple object mimic for attribute access if call_tool expects it
            # (This part remains the same, just moved inside the task creation loop)
            class ToolCall:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
                    if 'function' in kwargs and isinstance(kwargs['function'], dict):
                        self.function = type('Function', (), kwargs['function'])()

            tool_call_obj = ToolCall(**tool_call_dict)
            tool_tasks.append(call_tool(tool_call_obj))

        # Execute tool calls concurrently
        tool_results = await asyncio.gather(*tool_tasks)

        # Append tool results message(s) for the next API call
        tool_message = {
            "role": "tool",
            "content": None, # Content is not used when tool_calls is present in assistant message
                             # Instead, individual tool results are added
        }
        # OpenAI expects one message per tool result
        for result in tool_results:
             chat_messages.append({
                 "role": "tool",
                 "tool_call_id": result["tool_call_id"],
                 "name": result["name"],
                 "content": result["output"],
             })

    # Update session history after loop finishes
    cl.user_session.set("chat_messages", chat_messages)
