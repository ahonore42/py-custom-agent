"""
Main entry point for autonomous AI agent
"""

import sys
import asyncio

from .config import Config
from .agent import OllamaAgent
from .client import WebSocketClient
from .utils import setup_logging


def print_banner():
    """Print application banner"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║              AGENT v1.0                                            ║
║              Powered by Ollama                                     ║
╚════════════════════════════════════════════════════════════════════╝
    """)


async def main():
    """Main application entry point"""
    print_banner()
    
    # Validate configuration
    is_valid, error_msg = Config.validate()
    if not is_valid:
        print(f"\n❌ Configuration Error: {error_msg}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    # Display configuration
    Config.display_config()
    print()
    
    # Setup logging
    logger = setup_logging(
        Config.LOG_LEVEL,
        Config.LOG_FILE,
        Config.ENABLE_CONSOLE_LOG
    )
    
    logger.info("Starting autonomous AI agent")
    
    # Initialize AI agent
    try:
        agent = OllamaAgent(logger)
    except Exception as e:
        logger.error(f"Failed to initialize AI agent: {e}")
        sys.exit(1)
    
    # Test Ollama connection
    if not agent.test_connection():
        logger.error("Cannot connect to Ollama. Exiting.")
        print("\n❌ Cannot connect to Ollama")
        print("\nMake sure Ollama is running:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Verify model is available: ollama list")
        print(f"  3. Pull model if needed: ollama pull {Config.OLLAMA_MODEL}")
        sys.exit(1)
    
    # Initialize WebSocket client
    client = WebSocketClient(agent, logger)
    
    # Run the client
    try:
        logger.info("Starting WebSocket client...")
        print(f"\n{'Auto Mode' if Config.AUTO_MODE else 'Manual Mode'} enabled")
        print("Connecting to WebSocket...\n")
        await client.run()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
        print("\n\n⚠️  Agent stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Agent shutdown complete")
        print("\n✓ Agent shutdown complete")
        print(f"Session log saved to: {Config.LOG_FILE}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)