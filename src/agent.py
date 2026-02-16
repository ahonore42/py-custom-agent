"""
AI Agent with Ollama LLM integration
General-purpose agent for interpreting messages and generating responses
"""

import requests
import logging
from typing import Optional, Dict, Any

from .config import Config
from .utils import extract_json_from_text


class OllamaAgent:
    """AI Agent that uses Ollama LLM to interpret messages and decide responses"""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the AI agent
        
        Args:
            logger: Logger instance for logging
        """
        self.logger = logger
        self.model = Config.OLLAMA_MODEL
        self.api_url = Config.OLLAMA_API_URL
        self.timeout = Config.OLLAMA_TIMEOUT
        self.temperature = Config.OLLAMA_TEMPERATURE
        self.system_prompt = Config.get_system_prompt()
        
        self.logger.info(f"Agent initialized with model: {self.model}")
        
    def query_llm(self, prompt: str) -> Optional[str]:
        """
        Query Ollama LLM and get response
        
        Args:
            prompt: User prompt to send to LLM
        
        Returns:
            LLM response text or None if error
        """
        self.logger.debug(f"Querying LLM with prompt: {prompt[:100]}...")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "system": self.system_prompt,
                "options": {
                    "temperature": self.temperature
                }
            }
            
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get("response", "").strip()
            
            self.logger.debug(f"LLM responded with: {llm_response[:200]}...")
            return llm_response
            
        except requests.exceptions.Timeout:
            self.logger.error(f"LLM query timed out after {self.timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error querying LLM: {e}")
            return None
    
    def process_message(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Process an incoming message and generate a response
        
        Args:
            message: The message to process
        
        Returns:
            Response dictionary or None if unable to generate response
        """
        self.logger.info(f"Processing message: {message[:100]}...")
        
        # Query LLM
        llm_response = self.query_llm(message)
        
        if not llm_response:
            self.logger.error("Failed to get LLM response")
            return None
        
        # Extract JSON from LLM response
        response_data = extract_json_from_text(llm_response)
        
        if not response_data:
            self.logger.warning(f"Could not extract JSON from LLM response: {llm_response}")
            return None
        
        self.logger.info(f"Generated response: {response_data}")
        return response_data
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama API
        
        Returns:
            True if connection successful, False otherwise
        """
        self.logger.info("Testing Ollama connection...")
        
        try:
            # Try to query available models
            response = requests.get(
                self.api_url.replace("/api/generate", "/api/tags"),
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name') for m in models]
                
                if self.model in model_names or any(self.model in name for name in model_names):
                    self.logger.info(f"✓ Ollama connection successful, model '{self.model}' available")
                    return True
                else:
                    self.logger.error(f"✗ Model '{self.model}' not found. Available: {model_names}")
                    return False
            else:
                self.logger.error(f"✗ Ollama returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ Cannot connect to Ollama: {e}")
            self.logger.error("Make sure Ollama is running: ollama serve")
            return False