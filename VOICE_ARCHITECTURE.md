# 🎤 Voice Features - How It Works

## System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Human)                              │
│                        👤                                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ speaks
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  MICROPHONE INPUT                            │
│                       🎤                                     │
│  User speaks: "I want to apply for pension scheme"          │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ audio signal
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            SPEECH-TO-TEXT (Google Speech API)                │
│                       🔄                                     │
│  Converts: Audio → Text                                      │
│  Output: "I want to apply for pension scheme"               │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ text input
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  WELFARE AGENT (AI)                          │
│                       🤖                                     │
│  ┌─────────────────────────────────────────┐                │
│  │  1. PLANNING                             │                │
│  │     - Analyzes user query                │                │
│  │     - Determines what info needed        │                │
│  └─────────────────────────────────────────┘                │
│  ┌─────────────────────────────────────────┐                │
│  │  2. EXECUTING                            │                │
│  │     - Checks eligibility                 │                │
│  │     - Queries scheme database            │                │
│  │     - Retrieves relevant schemes         │                │
│  └─────────────────────────────────────────┘                │
│  ┌─────────────────────────────────────────┐                │
│  │  3. EVALUATING                           │                │
│  │     - Synthesizes results                │                │
│  │     - Checks for completeness            │                │
│  └─────────────────────────────────────────┘                │
│  ┌─────────────────────────────────────────┐                │
│  │  4. RESPONDING                           │                │
│  │     - Generates natural response         │                │
│  │     - Asks clarifying questions          │                │
│  └─────────────────────────────────────────┘                │
│                                                               │
│  Output: "I'd be happy to help. What is your age?"          │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ text response
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            TEXT-TO-SPEECH (Google TTS)                       │
│                       🔄                                     │
│  Converts: Text → Natural Voice                              │
│  Input: "I'd be happy to help. What is your age?"           │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ audio signal
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  SPEAKER OUTPUT                              │
│                       🔊                                     │
│  Agent speaks: "I'd be happy to help. What is your age?"    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ hears
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    USER (Human)                              │
│                        👤                                    │
│  Responds: "I am 65 years old"                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          └─────────► (Loop continues...)
```

## Conversation Example

### Full Voice Conversation Flow

```
Turn 1:
──────
🎤 USER SPEAKS: "I want to apply for a pension scheme"
       ↓ [Speech Recognition]
📝 AGENT HEARS: "I want to apply for a pension scheme"
       ↓ [Agent Processing]
       ├─ Planning: Need age and income info
       ├─ Executing: Query database for pension schemes
       ├─ Evaluating: Missing user profile data
       └─ Responding: Ask for age
🔊 AGENT SAYS: "I'd be happy to help you apply for a pension 
                scheme. To check your eligibility, I need some
                information. Could you tell me your age?"

Turn 2:
──────
🎤 USER SPEAKS: "I am 65 years old"
       ↓ [Speech Recognition]
📝 AGENT HEARS: "I am 65 years old"
       ↓ [Agent Processing]
       ├─ Planning: Store age, need income
       ├─ Executing: Update user profile
       ├─ Evaluating: Still need income info
       └─ Responding: Ask for income
🔊 AGENT SAYS: "Great! And what is your annual income?"

Turn 3:
──────
🎤 USER SPEAKS: "My income is around 30000 rupees per year"
       ↓ [Speech Recognition]
📝 AGENT HEARS: "My income is around 30000 rupees per year"
       ↓ [Agent Processing]
       ├─ Planning: Check eligibility with age + income
       ├─ Executing: Run eligibility checker
       ├─ Evaluating: Found matching schemes
       └─ Responding: Provide scheme details
🔊 AGENT SAYS: "Based on your age of 65 years and annual income
                of 30,000 rupees, you are eligible for the 
                National Old Age Pension Scheme. This provides
                a monthly pension of 200-500 rupees..."
```

## Technology Stack

### Input Layer (Listening)
```
Microphone Hardware
       ↓
PyAudio (Audio Capture)
       ↓
SpeechRecognition Library
       ↓
Google Speech Recognition API
       ↓
Recognized Text (Indian Languages)
```

### Processing Layer (Thinking)
```
User Query Text
       ↓
Agent State Machine
       ├─ Memory Manager (Context)
       ├─ LLM Provider (Reasoning)
       ├─ Tools (Actions)
       └─ Voice Interface (I/O)
       ↓
Response Text
```

### Output Layer (Speaking)
```
Response Text
       ↓
Google Text-to-Speech (gTTS)
       ↓
MP3 Audio File (Temporary)
       ↓
pygame Mixer (Playback)
       ↓
Speaker Hardware
       ↓
Human Hears Natural Voice
```

## Language Support Matrix

| Language | Code | STT Support | TTS Support | Voice Quality |
|----------|------|-------------|-------------|---------------|
| English  | en   | ✅ Excellent | ✅ Excellent | Natural      |
| Telugu   | te   | ✅ Good      | ✅ Good      | Natural      |
| Tamil    | ta   | ✅ Good      | ✅ Good      | Natural      |
| Marathi  | mr   | ✅ Good      | ✅ Good      | Natural      |
| Bengali  | bn   | ✅ Good      | ✅ Good      | Natural      |
| Odia     | or   | ✅ Good      | ✅ Good      | Natural      |

## Voice Interface Modes

### 1. Local Voice (Recommended)
```
Features:
- Uses computer's microphone and speakers
- Free Google Speech API
- Free gTTS for natural voices
- No cloud setup needed
- Internet required for recognition

Command:
python main.py voice en local
```

### 2. Mock Voice (Testing)
```
Features:
- No audio hardware needed
- Text-based simulation
- For development/testing
- No internet required

Command:
python main.py voice en mock
```

### 3. Cloud Voice (Advanced)
```
Features:
- Google Cloud Speech-to-Text
- Google Cloud Text-to-Speech
- Requires credentials
- Premium quality
- Costs may apply

Command:
python main.py voice en cloud
```

## Error Handling & Fallbacks

```
User speaks unclear/noisy audio
       ↓
Speech Recognition attempts
       ├─ Try regional language (e.g., Telugu)
       │  └─ Success? → Proceed
       │      └─ Failed? ↓
       └─ Try English fallback
          └─ Success? → Proceed
              └─ Failed? → Ask user to repeat
```

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Speech Recognition | 1-3 seconds | Depends on internet speed |
| Agent Processing | 0.5-2 seconds | Depends on LLM provider |
| Speech Synthesis | 1-2 seconds | Depends on text length |
| Audio Playback | Real-time | Depends on response length |
| **Total per turn** | **3-8 seconds** | Feels natural in conversation |

## Memory & Context

The agent maintains conversation memory:

```
┌─────────────────────────────────┐
│   Conversation Memory            │
├─────────────────────────────────┤
│ Turn 1: User wants pension      │
│ Turn 2: User is 65 years old    │
│ Turn 3: Income is 30000         │
│                                  │
│ Profile Built:                   │
│   Age: 65                        │
│   Income: 30000                  │
│   Intent: Pension application    │
└─────────────────────────────────┘
         │
         ▼
Context used for next query
```

## Security & Privacy

- ✅ Speech processing uses Google's secure APIs
- ✅ No audio stored permanently
- ✅ Conversation memory in RAM only
- ✅ Temporary audio files deleted immediately
- ✅ No data sent to third parties (except Google APIs)

---

**The system provides a natural, human-like conversation experience!**
