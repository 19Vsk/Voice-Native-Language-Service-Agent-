# Quick Start - Voice Mode 🎤

Get your voice-enabled welfare agent running in 5 minutes!

## 🚀 Setup (5 minutes)

### Step 1: Install Dependencies (2 minutes)
```powershell
# Run the automatic setup script
python setup_voice.py
```

This will install all necessary packages including:
- Speech recognition libraries
- Text-to-speech engine
- Audio playback components

### Step 2: Test Your Setup (1 minute)
```powershell
# Test microphone and speakers
python test_voice.py
```

Follow the prompts to:
- ✅ Verify microphone is working
- ✅ Test speaker output
- ✅ Do a live speech test

### Step 3: Start Talking! (2 minutes)

#### For English Voice Mode:
```powershell
python main.py voice en local
```

#### For Telugu Voice Mode:
```powershell
python main.py voice te local
```

#### For Other Languages:
```powershell
# Tamil
python main.py voice ta local

# Marathi
python main.py voice mr local

# Bengali
python main.py voice bn local
```

## 🎤 How to Use Voice Mode

1. **Start the agent** with the command above
2. **Wait for the greeting** - The agent will say hello
3. **Speak your query** when you see "🎤 Listening..."
4. **Wait for response** - The agent will speak back to you
5. **Continue conversation** - Just keep speaking!
6. **Say "quit" or "exit"** to end the session

## 💬 Example Voice Queries

### English
- "I want to apply for a pension scheme"
- "Am I eligible for any welfare programs?"
- "How do I check my application status?"
- "I am 65 years old and my income is 30000 rupees"

### Telugu (తెలుగు)
- "నాకు పెన్షన్ స్కీమ్ కోసం దరఖాస్తు చేయవాలి"
- "నేను ఏ సహాయ కార్యక్రమాలకు అర్హుడను?"
- "నా వయస్సు 65 సంవత్సరాలు"

### Tamil (தமிழ்)
- "எனக்கு ஓய்வூதிய திட்டத்திற்கு விண்ணப்பிக்க வேண்டும்"
- "நான் எந்த நல திட்டங்களுக்கு தகுதியானவன்?"
- "என் வயது 65 ஆண்டுகள்"

### Marathi (मराठी)
- "मला निवृत्तीवेतन योजनेसाठी अर्ज करायचा आहे"
- "मी कोणत्या कल्याण कार्यक्रमांसाठी पात्र आहे?"
- "माझे वय 65 वर्षे आहे"

## 🔧 Troubleshooting

### Microphone Not Working?
1. Check Windows microphone settings
2. Make sure microphone is not muted
3. Try running `python test_voice.py` again

### Can't Hear the Agent?
1. Check speaker volume
2. Ensure speakers/headphones are connected
3. Test audio with `python test_voice.py`

### Speech Not Recognized?
1. **Speak clearly** and at normal pace
2. **Reduce background noise**
3. **Check internet** connection (required for Google Speech API)
4. Try switching to English if regional language fails

### Installation Issues?
See detailed troubleshooting in [VOICE_SETUP.md](VOICE_SETUP.md)

## 📝 Alternative Modes

### Text Mode (Type Instead of Speaking)
```powershell
python main.py interactive en
```
Then type your questions instead of speaking.

### Demo Mode (See Pre-programmed Examples)
```powershell
python main.py demo te
```

## 🎯 Next Steps

1. ✅ Try a simple query in voice mode
2. ✅ Test different languages
3. ✅ Have a full conversation about welfare schemes
4. ✅ Explore the agent's capabilities

## 📚 More Information

- **Full Setup Guide**: [VOICE_SETUP.md](VOICE_SETUP.md)
- **System Architecture**: [README.md](README.md)
- **Technical Details**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Need Help?** Run `python test_voice.py` to diagnose issues!
