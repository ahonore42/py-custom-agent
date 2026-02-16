"""
Autonomous AI Agent Package
General-purpose agent for WebSocket-based challenges using Ollama LLMs
"""

from .config import Config
from .agent import OllamaAgent
from .client import WebSocketClient
from .utils import setup_logging

__version__ = "1.0.0"
__all__ = ["Config", "OllamaAgent", "WebSocketClient", "setup_logging"]