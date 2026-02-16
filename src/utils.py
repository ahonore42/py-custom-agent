"""
Utility functions for autonomous AI agent
Includes logging, JSON extraction, and helper functions
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


def setup_logging(log_level: str, log_file: str, enable_console: bool = True) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        enable_console: Whether to enable console logging
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("ai_agent")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that may contain other content
    Handles LLM responses that include markdown formatting or extra text
    
    Args:
        text: Text that may contain JSON
    
    Returns:
        Parsed JSON dict or None if not found
    """
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Try to parse the whole text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    # Look for JSON objects (basic pattern)
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, text)
    
    for match in matches:
        try:
            obj = json.loads(match)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    
    # Look for nested JSON objects
    pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    matches = re.findall(pattern, text)
    
    for match in matches:
        try:
            obj = json.loads(match)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    
    return None


def format_timestamp() -> str:
    """Get formatted timestamp for logging"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def sanitize_for_display(text: str, max_length: int = 200) -> str:
    """
    Sanitize text for display (truncate if too long)
    
    Args:
        text: Text to sanitize
        max_length: Maximum length before truncation
    
    Returns:
        Sanitized text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def is_fragmented_message(data: Dict[str, Any]) -> bool:
    """
    Check if a message appears to be a fragment that needs reconstruction
    
    Args:
        data: Message data dictionary
    
    Returns:
        True if message appears to be fragmented
    """
    # Common fragmentation indicators
    fragment_keys = ['fragment', 'sequence', 'part', 'chunk', 'index']
    total_keys = ['total', 'total_fragments', 'total_parts', 'count']
    
    has_fragment_indicator = any(key in data for key in fragment_keys)
    has_total_indicator = any(key in data for key in total_keys)
    
    # Also check for timestamp-based fragmentation
    has_timestamp = 'timestamp' in data
    has_id = 'id' in data or 'message_id' in data
    
    return (has_fragment_indicator or has_total_indicator or 
            (has_timestamp and has_id))


def validate_json_structure(data: Any, required_keys: list = None) -> tuple[bool, Optional[str]]:
    """
    Validate JSON structure
    
    Args:
        data: Data to validate
        required_keys: List of required keys (optional)
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    if required_keys:
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    return True, None