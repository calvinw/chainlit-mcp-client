# Available OpenRouter models for the Chainlit MCP Client

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
