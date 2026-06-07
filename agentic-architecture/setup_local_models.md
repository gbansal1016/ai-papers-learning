# Setup Guide: Running ReAct Agent with Local Models

## Quick Start (5 minutes)

### 1. Install Ollama
```bash
# Download from: https://ollama.ai
# Or on macOS with Homebrew:
brew install ollama
```

### 2. Pull a Model
```bash
ollama pull mistral
```

Available models:
- `mistral` - Fast, capable, **RECOMMENDED**
- `neural-chat` - Optimized for chat
- `llama2` - More capable, slower
- `dolphin-mixtral` - Very capable

### 3. Start Ollama Server
```bash
ollama serve
```

You should see:
```
serving on http://127.0.0.1:11434
```

**Leave this running in a terminal!**

### 4. In Another Terminal, Run the Agent
```bash
cd /Users/gaurav/Documents/Claude/workspace/agentic-architecture

# Verify configuration (should have USE_LOCAL_MODEL = True)
cat code/react_agent.py | grep "USE_LOCAL_MODEL"

# Run the agent
python code/react_agent.py
```

### 5. Test Query
When prompted, try:
```
I want to buy a laptop but I'm not sure which one. What do you recommend?
```

## What's Actually Happening

```
┌─────────────────────────────────────────────────────────────┐
│ YOUR COMPUTER                                               │
│                                                             │
│  Terminal 1: ollama serve                                  │
│  ├─ Listening on: http://localhost:11434/v1               │
│  └─ Running model: mistral (in memory)                    │
│                                                             │
│  Terminal 2: python react_agent.py                         │
│  ├─ Creates Anthropic client                              │
│  ├─ Points base_url → http://localhost:11434/v1          │
│  └─ Sends queries to local Mistral                         │
│      ↓                                                      │
│      Mistral processes locally (NO internet needed!)      │
│      ↓                                                      │
│      Returns response to your agent                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Understanding the Configuration

In `react_agent.py` at the top:

```python
USE_LOCAL_MODEL = True  # ← Change this flag

if USE_LOCAL_MODEL:
    # Using Ollama on your computer
    client = Anthropic(
        api_key="not-needed",
        base_url="http://localhost:11434/v1"
    )
    MODEL_NAME = "mistral"  # Your model choice

else:
    # Using Anthropic API (requires API key)
    client = Anthropic()
    MODEL_NAME = "claude-3-5-sonnet-20241022"
```

### Key Points:
- **USE_LOCAL_MODEL = True** → Use local Ollama
- **USE_LOCAL_MODEL = False** → Use Anthropic API (needs API key)
- **base_url** → Where Ollama is listening
- **MODEL_NAME** → Which model to use

## Troubleshooting

### "Connection refused" Error
```python
# Error: [Errno 61] Connection refused
```

**Solution:**
- Make sure `ollama serve` is running in another terminal
- Check: http://localhost:11434 in your browser should load

### "Model not found" Error
```python
# Error: model "mistral" not found
```

**Solution:**
```bash
ollama pull mistral
ollama list  # See what you have
```

### "Permission denied" on Ollama
```bash
brew reinstall ollama
# Then try: ollama serve again
```

### Agent is Very Slow
**Cause:** Ollama might be using CPU instead of GPU

**Check:**
```bash
# In the ollama serve terminal, look for:
# "AMD GPU" or "NVIDIA GPU" or "loaded..."
# If it says "CPU", your computer is using CPU (much slower)
```

**Solution:**
- Use a smaller model: `ollama pull neural-chat`
- Or use a faster CPU (i7/i9 preferred)
- Or upgrade to GPU-enabled Ollama

### Want to Switch Models?
```bash
# First, pull the new model
ollama pull llama2

# Then, edit react_agent.py:
MODEL_NAME = "llama2"  # ← Change this

# Run again
python code/react_agent.py
```

## Comparing Models

| Model | Size | Speed | Quality | Memory |
|-------|------|-------|---------|--------|
| mistral | 7B | 🟢 Fast | 🟢 Good | 5GB |
| neural-chat | 7B | 🟢 Fast | 🟢 Good | 5GB |
| llama2 | 7B | 🟡 Medium | 🟡 Better | 7GB |
| dolphin-mixtral | 46B | 🔴 Slow | 🟢 Excellent | 25GB |

**Recommendation:** Start with `mistral` (fast, good quality)

## Comparing Modes

### Local Model (USE_LOCAL_MODEL = True)
✅ **Pros:**
- Free (no API costs)
- Works offline
- Fast local inference
- Privacy (data stays on computer)

❌ **Cons:**
- Models are less capable than Claude
- Uses your computer's resources
- Slower than API on older machines

### Anthropic API (USE_LOCAL_MODEL = False)
✅ **Pros:**
- Best quality (Claude models)
- Works on any computer
- Constant updates

❌ **Cons:**
- Costs money
- Requires internet
- Data sent to Anthropic
- Requires API key

## Production Recommendation

For production ReAct agents:
```python
# Use this logic
USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
```

Then you can switch without code changes:
```bash
# Use local
USE_LOCAL_MODEL=true python react_agent.py

# Use Anthropic
USE_LOCAL_MODEL=false ANTHROPIC_API_KEY=sk-... python react_agent.py
```

## Next Steps

1. ✅ Install Ollama and run `ollama serve`
2. ✅ Run `python test_local_model.py` to verify setup
3. ✅ Run `python code/react_agent.py` to see the agent work
4. ✅ Read `LOCAL_MODELS_EXPLAINED.md` to understand base_url
5. ✅ Try modifying the system prompt in the agent
6. ✅ Add your own tools

## Advanced: Using Other Local Runners

If you prefer not to use Ollama:

### LM Studio (GUI)
```python
client = Anthropic(base_url="http://localhost:1234/v1")
MODEL_NAME = "your-model-name"
```

### vLLM
```bash
vllm serve mistral-7b
```
```python
client = Anthropic(base_url="http://localhost:8000/v1")
```

### Text Generation WebUI
```bash
python server.py --listen
```
```python
client = Anthropic(base_url="http://localhost:5000/v1")
```

## Summary

| Step | Command | Terminal |
|------|---------|----------|
| 1. Install | `brew install ollama` | Term 1 |
| 2. Pull model | `ollama pull mistral` | Term 1 |
| 3. Start server | `ollama serve` | Term 1 |
| 4. Test setup | `python test_local_model.py` | Term 2 |
| 5. Run agent | `python code/react_agent.py` | Term 2 |

**That's it! Your local ReAct agent is running.** 🎉
