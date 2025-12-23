# Voice Setup Guide for Welfare Agent

This guide will help you set up the voice capabilities so your welfare agent can speak like a human and listen to what humans say.

## 🎯 Features

Your welfare agent now supports:
- **Speech-to-Text (STT)**: Listen to user voice input in multiple Indian languages
- **Text-to-Speech (TTS)**: Respond with natural human-like voice
- **Multi-language Support**: Telugu, Tamil, Marathi, Bengali, Odia, and English
- **Real-time Conversation**: Natural back-and-forth dialogue

## 📋 Prerequisites

### For Windows:

1. **Python 3.8 or higher** - Already installed if you're running the project

2. **PyAudio** - Required for microphone access
   - Download the appropriate wheel file from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Or we'll install it via the script below

3. **Working Microphone** - Built-in laptop mic or external USB microphone

4. **Internet Connection** - Required for Google Speech Recognition API (free tier)

## 🚀 Installation

### Option 1: Automatic Setup (Recommended)

Run the setup script:
```powershell
python setup_voice.py
```

### Option 2: Manual Setup

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. Install PyAudio manually:
```powershell
# For Windows with Python 3.11 (64-bit)
pip install pipwin
pipwin install pyaudio
```

3. Test your installation:
```powershell
python -c "import speech_recognition; import gtts; import pygame; print('✅ All voice libraries installed!')"
```

## 🎤 Usage

### Voice Mode (Full Speech Interaction)

Start the agent in voice mode:
```powershell
# English voice mode
python main.py voice en local

# Telugu voice mode
python main.py voice te local

# Tamil voice mode
python main.py voice ta local

# Marathi voice mode
python main.py voice mr local
```

**How it works:**
1. The agent will greet you with a welcome message
2. When you see "🎤 Listening...", speak your query
3. The agent will process your speech and respond verbally
4. Say "quit", "exit", or "bye" to end the session

### Text Mode (Traditional)

If you prefer typing:
```powershell
python main.py interactive en
```

### Demo Mode

Run a predefined demo:
```powershell
python main.py demo te
```

## 🌐 Supported Languages

| Language | Code | Example Query |
|----------|------|---------------|
| English | `en` | "I want to apply for a pension scheme" |
| Telugu | `te` | "నాకు పెన్షన్ స్కీమ్ కోసం దరఖాస్తు చేయవాలి" |
| Tamil | `ta` | "எனக்கு ஓய்வூதிய திட்டத்திற்கு விண்ணப்பிக்க வேண்டும்" |
| Marathi | `mr` | "मला निवृत्तीवेतन योजनेसाठी अर्ज करायचा आहे" |
| Bengali | `bn` | "আমি পেনশন স্কিমের জন্য আবেদন করতে চাই" |
| Odia | `or` | "ମୁଁ ପେନସନ ଯୋଜନା ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛି" |

## 🔧 Troubleshooting

### Microphone Not Working
```powershell
# Test your microphone
python -m speech_recognition
```

### PyAudio Installation Issues
```powershell
# Alternative installation methods:
pip install pipwin
pipwin install pyaudio

# Or download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### No Sound Output
- Check your system volume
- Ensure speakers/headphones are connected
- Try running: `python -c "import pygame; pygame.mixer.init(); print('✅ Audio OK')"`

### Speech Recognition Not Working
- Check internet connection (Google Speech API requires internet)
- Speak clearly and close to the microphone
- Reduce background noise
- Try adjusting microphone sensitivity in Windows settings

### Language Not Recognized
- Ensure you're using the correct language code
- Try speaking in English if regional language fails
- Check that the language is supported by Google Speech Recognition

## 💡 Tips for Best Results

1. **Microphone Position**: Keep microphone 6-12 inches from your mouth
2. **Background Noise**: Use in a quiet environment
3. **Speaking**: Speak clearly at normal pace
4. **Internet**: Stable connection improves recognition accuracy
5. **Language Mixing**: The system can handle code-switching between regional language and English

## 📝 Example Conversation

```
=== 🎤 Welfare Agent Voice Mode (Language: en) ===

🔊 Speaking: Hello! I am your welfare assistant. How can I help you today?

🎤 Listening... (speak now)
✅ You said: I want to apply for a pension scheme

🔊 Speaking: I'd be happy to help you apply for a pension scheme. To check your eligibility, I need some information. Could you tell me your age?

🎤 Listening... (speak now)
✅ You said: I am 62 years old

🔊 Speaking: Great! And what is your annual income?

🎤 Listening... (speak now)
✅ You said: My income is around 30000 rupees per year

🔊 Speaking: Based on your age of 62 years and annual income of 30,000 rupees, you are eligible for the Senior Citizen Pension Scheme...
```

## 🎯 Next Steps

1. Test with the demo mode first
2. Try text mode to understand the agent's capabilities
3. Switch to voice mode for full speech interaction
4. Experiment with different languages
5. Customize the agent's responses in `src/agent/core.py`

## 🆘 Support

If you encounter issues:
1. Check the logs in the terminal
2. Verify all dependencies are installed
3. Test individual components (microphone, speakers, internet)
4. Review the error messages for specific guidance

Enjoy your voice-enabled welfare agent! 🎉
