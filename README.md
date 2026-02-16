# Autonomous AI Agent

A general-purpose autonomous AI agent that uses local LLMs (via Ollama) to solve WebSocket-based challenges. The agent connects to a WebSocket endpoint, interprets incoming messages using an LLM, and generates appropriate JSON responses.

## Features

- 🤖 **Fully Autonomous** - Agent makes decisions without human intervention
- 🔒 **100% Local** - Runs entirely on your machine via Ollama (no cloud APIs)
- 🧩 **Fragment Reconstruction** - Automatically assembles fragmented messages
- ⚙️ **Highly Configurable** - Environment-based configuration for any use case
- 📝 **Comprehensive Logging** - Full audit trail of all interactions
- 🎯 **Dual Mode** - Auto mode (AI decides) or manual mode (you control)
- 🚀 **Production Ready** - Proper error handling, validation, and testing

## Architecture

```
WebSocket Server ←→ Agent Client ←→ Ollama LLM (Local)
```

The agent:

1. Connects to a WebSocket endpoint
2. Receives and optionally reconstructs fragmented messages
3. Sends each message to local Ollama LLM for interpretation
4. Extracts JSON from LLM response
5. Sends formatted JSON back to the WebSocket server

## Prerequisites

- **Python 3.8+**
- **Ollama** installed and running
- A powerful Ollama model installed

## Quick Start

### 1. Install Ollama

**macOS/Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### 2. Pull a Model

```bash
# Recommended: GLM-4.7-Flash (fast, excellent reasoning)
ollama pull glm-4.7-flash

# Other options:
ollama pull llama3.1:70b    # Most powerful (requires 40GB+ RAM)
ollama pull qwen2.5:14b     # Excellent reasoning
ollama pull mistral:7b      # Fast and capable
```

### 3. Clone and Setup

```bash
git clone https://github.com/ahonore42/neon-agent.git
cd neon-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required settings:**

- `WEBSOCKET_URI` - The WebSocket endpoint to connect to
- `SYSTEM_PROMPT` or `SYSTEM_PROMPT_FILE` - Instructions for the LLM
- `OLLAMA_MODEL` - The model you pulled

### 5. Run

```bash
# Start Ollama (in separate terminal)
ollama serve

# Run the agent
python -m src.main
```

## Configuration

All configuration is done via the `.env` file. See `.env.example` for all available options.

### Key Configuration Options

#### Ollama Settings

```env
OLLAMA_MODEL=glm-4.7-flash:latest  # Which model to use
OLLAMA_TEMPERATURE=0.7              # 0.0-1.0, lower = more deterministic
OLLAMA_TIMEOUT=60                   # Request timeout in seconds
```

#### WebSocket Settings

```env
WEBSOCKET_URI=ws://example.com/challenge  # Target WebSocket
WEBSOCKET_TIMEOUT=30                       # Connection timeout
```

#### System Prompt

The system prompt tells the LLM how to behave. Two options:

**Option 1: Direct in .env**

```env
SYSTEM_PROMPT=You are an AI agent. Analyze messages and respond with valid JSON only.
```

**Option 2: Load from file**

```env
SYSTEM_PROMPT_FILE=prompts/my_prompt.txt
```

#### Agent Behavior

```env
AUTO_MODE=true                         # true = AI decides, false = manual input
ENABLE_FRAGMENT_RECONSTRUCTION=true    # Auto-assemble fragmented messages
```

#### Logging

```env
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/agent_session.log        # Log file path
ENABLE_CONSOLE_LOG=true                # Show logs in console
```

## Project Structure

```
neon-agent/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── agent.py             # AI agent logic (Ollama integration)
│   ├── client.py            # WebSocket client
│   ├── utils.py             # Utilities (logging, JSON extraction)
│   └── main.py              # Entry point
├── logs/                    # Session logs (auto-created)
├── .env                     # Your configuration (not in git)
├── .env.example             # Example configuration
├── .gitignore
├── requirements.txt
└── README.md
```

## Usage Examples

### Autonomous Mode (Default)

```bash
# Agent runs fully autonomously
python -m src.main
```

The agent will:

- Connect to WebSocket
- Receive messages
- Consult LLM for each message
- Extract JSON from LLM response
- Send response automatically

### Manual Mode

```bash
# Set in .env: AUTO_MODE=false
python -m src.main
```

In manual mode, you provide the JSON response for each message.

### Custom System Prompt

Create a file with your system prompt:

```bash
mkdir prompts
cat > prompts/my_challenge.txt << 'EOF'
You are solving a puzzle that requires authentication.

When you receive a message asking to "press" or "enter" digits:
- Respond with: {"type": "enter_digits", "digits": "value"}

When you receive a message asking to "speak" or "transmit" text:
- Respond with: {"type": "speak_text", "text": "value"}

Respond with ONLY valid JSON, no other text.
EOF
```

Then set in `.env`:

```env
SYSTEM_PROMPT_FILE=prompts/my_challenge.txt
```

## How It Works

### Message Flow

1. **WebSocket receives message**

   ```
   {"fragment": 1, "total": 3, "text": "Hello"}
   ```

2. **Fragment reconstruction** (if enabled)
   - Collects fragments by ID/sequence
   - Waits for all fragments
   - Reconstructs: "Hello world this is a test"

3. **LLM processing**
   - Sends message + system prompt to Ollama
   - LLM analyzes and generates response
   - Example LLM output:

   ```
   Based on the message, here is the response:
   {"type": "speak_text", "text": "Hello"}
   ```

4. **JSON extraction**
   - Extracts JSON from LLM response
   - Validates structure
   - Result: `{"type": "speak_text", "text": "Hello"}`

5. **Send response**
   - Sends JSON to WebSocket
   - Logs interaction

## Troubleshooting

### Cannot connect to Ollama

```bash
# Make sure Ollama is running
ollama serve

# Verify it's responding
curl http://localhost:11434/api/tags

# Check your model is installed
ollama list
```

### Model not found

```bash
# Pull the model
ollama pull glm-4.7-flash

# Verify it's available
ollama list
```

### WebSocket connection fails

- Check `WEBSOCKET_URI` in `.env`
- Verify the endpoint is reachable
- Review logs in `logs/agent_session.log`

### LLM returns invalid JSON

- Try a more powerful model (70B instead of 8B)
- Lower the temperature: `OLLAMA_TEMPERATURE=0.3`
- Improve your system prompt with more explicit JSON examples
- Check logs to see what the LLM actually returned

### Messages not reconstructing properly

- Set `ENABLE_FRAGMENT_RECONSTRUCTION=true`
- Check logs to see fragment collection progress
- Verify fragments have sequence/timestamp/index fields

## Performance Tips

### Model Selection

- **For speed**: `mistral:7b`, `llama3.1:8b`
- **For accuracy**: `llama3.1:70b`, `qwen2.5:14b`, `glm-4.7-flash`
- **For limited RAM**: `phi3:mini` (4GB), `llama3.1:8b` (8GB)

### Temperature Settings

- **Logic puzzles**: 0.1 - 0.3 (deterministic)
- **General tasks**: 0.5 - 0.7 (balanced)
- **Creative tasks**: 0.8 - 1.0 (creative)

### Timeout Settings

- **Fast models**: 30s
- **Large models**: 60-120s

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## Logs

All interactions are logged to `logs/agent_session.log`:

```
[2024-02-16 22:30:45] [INFO] Starting autonomous AI agent
[2024-02-16 22:30:46] [INFO] ✓ Ollama connection successful
[2024-02-16 22:30:47] [INFO] ✓ Connected to WebSocket
[2024-02-16 22:30:48] [INFO] Processing: Hello, identify yourself
[2024-02-16 22:30:49] [INFO] Generated response: {"type": "speak_text", "text": "AI Agent"}
[2024-02-16 22:30:50] [INFO] Sending: {"type": "speak_text", "text": "AI Agent"}
```

## License

MIT License

## Author

Adam Honore

- GitHub: [@ahonore42](https://github.com/ahonore42)
- LinkedIn: [adam-honore-software-engineer](https://linkedin.com/in/adam-honore-software-engineer)

## Contributing

Contributions welcome! Please open an issue or PR.

## Acknowledgments

- Built with [Ollama](https://ollama.com/) for local LLM inference
- Uses [websockets](https://websockets.readthedocs.io/) library
