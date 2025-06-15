"""
Simple Model Persistence for Chainlit MCP Client
Only saves/loads the selected model name to/from localStorage

Requires: public/model_manager.js and config.toml with:
[UI]
custom_js = '/public/model_manager.js'
"""

import json
import asyncio
import chainlit as cl
from models import OPENROUTER_MODELS, DEFAULT_MODEL

class ModelManager:
    """Simple manager for persisting just the model selection"""
    
    def __init__(self):
        self.loaded_model = None
        
    async def save_model(self, model_name):
        """Save model name to localStorage"""
        print(f"🟦 PYTHON: Saving model: {model_name}")
        message = {"type": "SAVE_MODEL", "model": model_name}
        await cl.send_window_message(json.dumps(message))
    
    async def load_model(self):
        """Load model name from localStorage"""
        print("🟦 PYTHON: Requesting model from localStorage")
        message = {"type": "LOAD_MODEL"}
        await cl.send_window_message(json.dumps(message))
        await asyncio.sleep(0.3)  # Wait for response
        return self.loaded_model or DEFAULT_MODEL
    
    async def handle_window_message(self, message_str):
        """Handle incoming window messages from JavaScript"""
        try:
            message = json.loads(message_str)
            
            if message.get("type") == "MODEL_LOADED":
                model = message.get("model")
                print(f"🟦 PYTHON: Model loaded from localStorage: {model or 'NO MODEL'}")
                self.loaded_model = model
                
            elif message.get("type") == "MODEL_SAVED":
                success = message.get("success", False)
                model = message.get("model")
                if success:
                    print(f"🟦 PYTHON: Model successfully saved: {model}")
                else:
                    print("🟦 PYTHON: Failed to save model")
                    
        except json.JSONDecodeError:
            pass  # Ignore non-JSON messages
        except Exception as e:
            print(f"🔴 PYTHON: Error handling message: {e}")

# Global model manager
model_manager = ModelManager()

@cl.on_window_message
async def handle_model_message(message: str):
    """Handle window messages for model persistence"""
    await model_manager.handle_window_message(message)

async def save_selected_model(model_name):
    """Save the selected model"""
    if model_name in OPENROUTER_MODELS:
        await model_manager.save_model(model_name)

async def load_selected_model():
    """Load the selected model"""
    return await model_manager.load_model()
