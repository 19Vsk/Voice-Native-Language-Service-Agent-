# Quick Start Guide

## 5-Minute Setup

### 1. Clone and Install
```bash
cd welfare-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your settings (defaults are fine for demo)
```

### 3. Run Interactive Demo
```bash
python main.py
```

You'll see:
```
=== Welfare Agent (Language: te) ===
Type 'quit' to exit, 'status' to see agent state

You: <type your message in Telugu or English>
Agent: <responds in your language>
```

### 4. Try These Commands

**Interactive Mode:**
```
You: నాకు పెన్షన్ కోసం దరఖాస్తు చేయాలి
Agent: [provides pension eligibility info]

You: నా వయస్సు 65 సంవత్సరాలు
Agent: [updates profile]

You: నా ఆదాయం 40000
Agent: [recommends matching schemes]
```

**Status Check:**
```
You: status
Shows current agent state and memory

You: memory
Shows recent conversation history
```

### 5. Run Demo Scenario
```bash
python main.py demo
```

Automatically runs through demo interactions with expected output.

### 6. Evaluate System
```bash
python main.py evaluate
```

Runs test scenarios and shows success rates.

---

## Language Support

Change language in `main.py`:
```python
agent = WelfareAgent(language="ta")  # Tamil
agent = WelfareAgent(language="mr")  # Marathi
agent = WelfareAgent(language="bn")  # Bengali
```

Or at runtime:
```
You: మీరు తమిళ్‌లో మాట్లాడాలనుకుంటున్నారా?
Agent: [switches to Tamil]
```

---

## Enable Real Features

### Use OpenAI GPT
1. Get API key from https://openai.com/api
2. Update `main.py`:
```python
agent = WelfareAgent(
    llm_provider="openai",
    api_key="sk-..."
)
```

### Enable Voice Input
1. Ensure microphone connected
2. Update `main.py`:
```python
agent = WelfareAgent(voice_mode="local")
```
3. When prompted, speak your request in any language

### Use Google Cloud
1. Download credentials from Google Cloud Console
2. Set environment variable: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json`
3. Update `main.py`:
```python
agent = WelfareAgent(voice_mode="cloud")
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
```bash
# Ensure all dependencies installed
pip install -r requirements.txt
```

### Issue: API Key Error
```bash
# Check .env file exists and has correct keys
cat .env

# Or pass directly:
agent = WelfareAgent(api_key="sk-...")
```

### Issue: Voice Not Working
```bash
# Check microphone
python -c "import speech_recognition; print(speech_recognition.Microphone())"

# Use mock mode for testing
agent = WelfareAgent(voice_mode="mock")
```

### Issue: Slow Response
```bash
# Normal first-time response: 2-3 seconds
# Slow responses usually due to API latency
# Use mock LLM for testing:
agent = WelfareAgent(llm_provider="mock")
```

---

## Next Steps

1. **Read Architecture** → `docs/ARCHITECTURE.md`
2. **Review Evaluation** → `docs/EVALUATION.md`
3. **Integrate APIs** → Replace mock tools with real ones
4. **Deploy** → See deployment guide in README.md

---

## Support

- 📖 Full README: `README.md`
- 🏗️ Architecture Docs: `docs/ARCHITECTURE.md`
- ✅ Test Results: `docs/EVALUATION.md`
- 💬 Questions: Create an issue on GitHub
