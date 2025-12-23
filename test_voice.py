"""
Quick test script for voice capabilities
Run this to test if your microphone and speakers are working
"""
import asyncio
import sys

async def test_voice():
    """Test voice input and output"""
    print("\n" + "="*60)
    print("🎤 Voice Capability Test")
    print("="*60 + "\n")
    
    # Test imports
    print("1️⃣  Testing imports...")
    try:
        import speech_recognition as sr
        import pygame
        from gtts import gTTS
        print("   ✅ All required libraries are installed\n")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("\n   Please run: python setup_voice.py\n")
        return
    
    # Test microphone
    print("2️⃣  Testing microphone...")
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        print("   ✅ Microphone is accessible")
        
        print("\n   Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()[:5]):
            print(f"      [{index}] {name}")
        print()
    except Exception as e:
        print(f"   ❌ Microphone error: {e}\n")
        return
    
    # Test speakers
    print("3️⃣  Testing speakers...")
    try:
        import pygame
        pygame.mixer.init()
        print("   ✅ Audio output is working\n")
        pygame.mixer.quit()
    except Exception as e:
        print(f"   ❌ Audio error: {e}\n")
        return
    
    # Live test
    print("4️⃣  Live test")
    print("   This will test your microphone and speakers together.\n")
    
    choice = input("   Do you want to perform a live test? (y/n): ").strip().lower()
    
    if choice == 'y':
        from src.voice.interface import LocalVoiceInterface
        
        voice = LocalVoiceInterface()
        
        # Test TTS first
        print("\n   📢 Testing Text-to-Speech...")
        test_messages = {
            "en": "Hello! This is a test of the text to speech system. Can you hear me clearly?",
            "te": "నమస్కారం! ఇది టెక్స్ట్ టు స్పీచ్ సిస్టమ్ పరీక్ష. మీరు నన్ను స్పష్టంగా వినగలరా?",
            "ta": "வணக்கம்! இது உரையை பேச்சு அமைப்பின் சோதனை. என்னை தெளிவாகக் கேட்கிறீர்களா?",
        }
        
        lang = input("   Choose language (en/te/ta): ").strip() or "en"
        message = test_messages.get(lang, test_messages["en"])
        
        await voice.speak(message, lang)
        
        heard = input("\n   Did you hear the message clearly? (y/n): ").strip().lower()
        if heard == 'y':
            print("   ✅ Text-to-Speech is working!\n")
        else:
            print("   ⚠️  Check your speakers/headphones\n")
            return
        
        # Test STT
        print("   🎤 Testing Speech-to-Text...")
        print("   When prompted, say something like:")
        print(f"      - In English: 'I want to apply for a welfare scheme'")
        print(f"      - In Telugu: 'నాకు సహాయ స్కీమ్ కోసం దరఖాస్తు చేయవాలి'")
        print(f"      - In Tamil: 'எனக்கு நல திட்டத்திற்கு விண்ணப்பிக்க வேண்டும்'\n")
        
        input("   Press Enter when ready to speak...")
        
        text = await voice.listen(lang)
        
        if text:
            print(f"\n   ✅ Successfully recognized: '{text}'")
            
            # Echo it back
            echo_msg = f"You said: {text}"
            await voice.speak(echo_msg, "en")
            
            print("\n   ✅ Speech-to-Text is working!")
        else:
            print("\n   ⚠️  Could not recognize speech")
            print("      Possible issues:")
            print("      - Background noise too high")
            print("      - Microphone too far away")
            print("      - No internet connection (required for Google Speech API)")
    
    print("\n" + "="*60)
    print("✅ Voice test complete!")
    print("="*60)
    print("\nTo start the voice agent:")
    print("  python main.py voice en local")
    print("\nFor more help:")
    print("  See VOICE_SETUP.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_voice())
