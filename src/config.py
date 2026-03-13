"""
Centralized configuration for HealthLensBot.
Loads environment variables and initializes the OpenRouter client.
This module should be imported first to ensure env vars are set
before other modules (e.g., CrewAI) read them.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# --- OpenRouter / LiteLLM Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# CrewAI uses LiteLLM internally; these env vars tell it to route through OpenRouter
os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["OPENAI_MODEL_NAME"] = "openrouter/meta-llama/llama-3.3-70b-instruct"

# --- OpenAI-compatible client for direct tool calls ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Model IDs on OpenRouter ---
VISION_MODEL = "qwen/qwen2.5-vl-72b-instruct"
TEXT_MODEL = "meta-llama/llama-3.3-70b-instruct"
