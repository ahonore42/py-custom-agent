"""
WebSocket client for autonomous AI agent
Handles WebSocket connection, message processing, and fragment reconstruction
"""

import asyncio
import websockets
import json
import logging
from typing import Optional, Dict, Any, List

from .config import Config
from .agent import OllamaAgent
from .utils import is_fragmented_message


class WebSocketClient:
    """WebSocket client that manages connection and message handling"""
    
    def __init__(self, agent: OllamaAgent, logger: logging.Logger):
        """
        Initialize WebSocket client
        
        Args:
            agent: AI agent for processing messages
            logger: Logger instance
        """
        self.agent = agent
        self.logger = logger
        self.uri = Config.WEBSOCKET_URI
        self.timeout = Config.WEBSOCKET_TIMEOUT
        self.auto_mode = Config.AUTO_MODE
        self.enable_fragments = Config.ENABLE_FRAGMENT_RECONSTRUCTION
        
        # Fragment tracking
        self.fragments = {}
        self.message_buffer = []
        
    def reconstruct_fragments(self, fragments: List[Dict[str, Any]]) -> Optional[str]:
        """
        Reconstruct fragmented messages
        
        Args:
            fragments: List of fragment dictionaries
        
        Returns:
            Reconstructed message text or None
        """
        if not fragments:
            return None
        
        # Sort fragments by sequence/timestamp
        sorted_fragments = sorted(
            fragments,
            key=lambda x: x.get('sequence', x.get('timestamp', x.get('index', 0)))
        )
        
        # Extract text from each fragment
        texts = []
        for frag in sorted_fragments:
            # Try different common keys for message content
            text = (frag.get('text') or 
                   frag.get('content') or 
                   frag.get('message') or 
                   frag.get('data') or 
                   str(frag))
            if text:
                texts.append(str(text))
        
        if texts:
            reconstructed = ' '.join(texts)
            self.logger.info(f"Reconstructed message from {len(fragments)} fragments")
            return reconstructed
        
        return None
    
    async def handle_message(self, raw_message: str) -> Optional[str]:
        """
        Process incoming WebSocket message
        
        Args:
            raw_message: Raw message from WebSocket
        
        Returns:
            Processed message text or None if waiting for more fragments
        """
        self.logger.debug(f"Received raw message: {raw_message[:200]}...")
        
        # Try to parse as JSON
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError:
            # Not JSON, treat as plain text
            self.logger.debug("Message is plain text, not JSON")
            return raw_message
        
        # Store in buffer
        self.message_buffer.append(data)
        
        # Check if this is a fragment (if fragment reconstruction is enabled)
        if self.enable_fragments and is_fragmented_message(data):
            fragment_id = data.get('id', data.get('message_id', 'default'))
            
            if fragment_id not in self.fragments:
                self.fragments[fragment_id] = []
            
            self.fragments[fragment_id].append(data)
            
            # Check if we have all fragments
            total = data.get('total', data.get('total_fragments', data.get('count', 0)))
            current_count = len(self.fragments[fragment_id])
            
            if total > 0 and current_count >= total:
                # We have all fragments, reconstruct
                reconstructed = self.reconstruct_fragments(self.fragments[fragment_id])
                self.fragments[fragment_id] = []  # Clear fragments
                return reconstructed
            else:
                # Still waiting for more fragments
                self.logger.info(f"Fragment {current_count}/{total} received, waiting...")
                return None
        
        # Not a fragment, extract message content
        if isinstance(data, dict):
            message = (data.get('message') or 
                      data.get('text') or 
                      data.get('content') or 
                      str(data))
            return message
        
        return str(data)
    
    async def send_response(self, websocket, response_data: Dict[str, Any]):
        """
        Send response to WebSocket
        
        Args:
            websocket: WebSocket connection
            response_data: Response data to send
        """
        response_json = json.dumps(response_data)
        self.logger.info(f"Sending: {response_json}")
        await websocket.send(response_json)
    
    async def run(self):
        """Main client loop - connects and processes messages"""
        self.logger.info(f"Connecting to WebSocket: {self.uri}")
        
        try:
            async with websockets.connect(self.uri) as websocket:
                self.logger.info("✓ Connected to WebSocket")
                
                async for raw_message in websocket:
                    # Process message (handle fragments)
                    processed_message = await self.handle_message(raw_message)
                    
                    # If waiting for more fragments, continue
                    if processed_message is None:
                        continue
                    
                    self.logger.info(f"Processing: {processed_message[:200]}...")
                    
                    if self.auto_mode:
                        # Autonomous mode - use AI to decide response
                        self.logger.info("→ Consulting AI agent...")
                        response_data = self.agent.process_message(processed_message)
                        
                        if response_data:
                            await self.send_response(websocket, response_data)
                        else:
                            self.logger.error("Agent could not generate response")
                    else:
                        # Manual mode - wait for user input
                        print("\n" + "="*70)
                        print("MESSAGE RECEIVED:")
                        print("-"*70)
                        print(processed_message)
                        print("-"*70)
                        print("\nEnter JSON response (or 'quit'): ")
                        
                        user_input = input().strip()
                        if user_input.lower() == 'quit':
                            break
                        
                        try:
                            response_data = json.loads(user_input)
                            await self.send_response(websocket, response_data)
                        except json.JSONDecodeError:
                            self.logger.error("Invalid JSON input")
                
        except websockets.exceptions.WebSocketException as e:
            self.logger.error(f"WebSocket error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise