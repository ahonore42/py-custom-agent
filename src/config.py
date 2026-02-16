"""
Configuration management for autonomous AI agent
Loads settings from environment variables with validation
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class with environment variable loading and validation"""
    
    # Ollama Configuration
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    
    # WebSocket Configuration
    WEBSOCKET_URI: str = os.getenv("WEBSOCKET_URI", "")
    WEBSOCKET_TIMEOUT: int = int(os.getenv("WEBSOCKET_TIMEOUT", "30"))
    
    # System Prompt Configuration
    SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", "")
    SYSTEM_PROMPT_FILE: str = os.getenv("SYSTEM_PROMPT_FILE", "")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/agent_session.log")
    ENABLE_CONSOLE_LOG: bool = os.getenv("ENABLE_CONSOLE_LOG", "true").lower() == "true"
    
    # Agent Behavior Configuration
    AUTO_MODE: bool = os.getenv("AUTO_MODE", "true").lower() == "true"
    ENABLE_FRAGMENT_RECONSTRUCTION: bool = os.getenv("ENABLE_FRAGMENT_RECONSTRUCTION", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate required configuration
        Returns: (is_valid, error_message)
        """
        if not cls.WEBSOCKET_URI:
            return False, "WEBSOCKET_URI is required in .env file"
        
        if not cls.SYSTEM_PROMPT and not cls.SYSTEM_PROMPT_FILE:
            return False, "Either SYSTEM_PROMPT or SYSTEM_PROMPT_FILE must be set"
        
        return True, None
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """
        Get system prompt from environment or file
        """
        # If direct system prompt is provided, use it
        if cls.SYSTEM_PROMPT:
            return cls.SYSTEM_PROMPT
        
        # Otherwise, load from file
        if cls.SYSTEM_PROMPT_FILE:
            try:
                with open(cls.SYSTEM_PROMPT_FILE, 'r') as f:
                    return f.read().strip()
            except FileNotFoundError:
                raise ValueError(f"System prompt file not found: {cls.SYSTEM_PROMPT_FILE}")
            except Exception as e:
                raise ValueError(f"Error reading system prompt file: {e}")
        
        return ""
    
    @classmethod
    def display_config(cls):
        """Display current configuration (hiding sensitive data)"""
        print("="*70)
        print("AI AGENT CONFIGURATION")
        print("="*70)
        print(f"Ollama Model:        {cls.OLLAMA_MODEL}")
        print(f"Ollama API URL:      {cls.OLLAMA_API_URL}")
        print(f"Temperature:         {cls.OLLAMA_TEMPERATURE}")
        print(f"WebSocket URI:       {cls.WEBSOCKET_URI}")
        print(f"Auto Mode:           {cls.AUTO_MODE}")
        print(f"Fragment Recon:      {cls.ENABLE_FRAGMENT_RECONSTRUCTION}")
        print(f"Log Level:           {cls.LOG_LEVEL}")
        print(f"Log File:            {cls.LOG_FILE}")
        print("="*70)