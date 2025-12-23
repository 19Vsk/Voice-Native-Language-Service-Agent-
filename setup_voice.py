"""
Setup script for voice capabilities
This script helps install and test all necessary voice components
"""
import subprocess
import sys
import platform

def run_command(command, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎤 Welfare Agent Voice Setup 🔊                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Detect system
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}\n")
    
    # Step 1: Upgrade pip
    run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )
    
    # Step 2: Install basic requirements
    print("\n" + "="*60)
    print("📦 Installing basic dependencies...")
    print("="*60)
    
    packages = [
        ("SpeechRecognition", "Speech recognition library"),
        ("gtts", "Google Text-to-Speech"),
        ("pygame", "Audio playback"),
        ("python-dotenv", "Environment variables"),
    ]
    
    for package, description in packages:
        run_command(
            f"{sys.executable} -m pip install {package}",
            f"Installing {description}"
        )
    
    # Step 3: Install PyAudio (Windows specific handling)
    print("\n" + "="*60)
    print("🎙️ Installing PyAudio (for microphone access)...")
    print("="*60)
    
    if platform.system() == "Windows":
        # Try pipwin first
        if run_command(f"{sys.executable} -m pip install pipwin", "Installing pipwin helper"):
            run_command(f"{sys.executable} -m pipwin install pyaudio", "Installing PyAudio via pipwin")
        else:
            # Fallback to regular pip
            run_command(f"{sys.executable} -m pip install pyaudio", "Installing PyAudio via pip")
    else:
        # Linux/Mac
        run_command(f"{sys.executable} -m pip install pyaudio", "Installing PyAudio")
    
    # Step 4: Install remaining requirements
    print("\n" + "="*60)
    print("📋 Installing remaining project requirements...")
    print("="*60)
    
    run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements.txt"
    )
    
    # Step 5: Test installations
    print("\n" + "="*60)
    print("🧪 Testing installations...")
    print("="*60)
    
    all_ok = True
    
    tests = [
        ("speech_recognition", "SpeechRecognition"),
        ("gtts", "gTTS"),
        ("pygame", "pygame"),
        ("dotenv", "python-dotenv"),
    ]
    
    for module, name in tests:
        if not test_import(module, name):
            all_ok = False
    
    # Special test for PyAudio
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"✅ PyAudio is installed ({device_count} audio devices detected)")
    except Exception as e:
        print(f"❌ PyAudio test failed: {e}")
        all_ok = False
    
    # Step 6: Test microphone
    print("\n" + "="*60)
    print("🎤 Testing microphone access...")
    print("="*60)
    
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        print("✅ Microphone access OK")
        
        print("\nAvailable microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  [{index}] {name}")
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        all_ok = False
    
    # Step 7: Test audio output
    print("\n" + "="*60)
    print("🔊 Testing audio output...")
    print("="*60)
    
    try:
        import pygame
        pygame.mixer.init()
        print("✅ Audio output OK")
        pygame.mixer.quit()
    except Exception as e:
        print(f"❌ Audio output test failed: {e}")
        all_ok = False
    
    # Final results
    print("\n" + "="*60)
    if all_ok:
        print("✅ ✅ ✅  ALL TESTS PASSED! ✅ ✅ ✅")
        print("="*60)
        print("""
🎉 Voice capabilities are ready!

To start using voice mode:

1. For English:
   python main.py voice en local

2. For Telugu:
   python main.py voice te local

3. For Tamil:
   python main.py voice ta local

See VOICE_SETUP.md for more information.
        """)
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*60)
        print("""
Please review the errors above and:

1. On Windows, try installing PyAudio manually:
   - Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Install with: pip install <downloaded_file.whl>

2. Check your microphone in Windows Settings:
   - Settings > Privacy > Microphone
   - Ensure microphone access is enabled

3. For other issues, see VOICE_SETUP.md for troubleshooting

4. You can still use text mode:
   python main.py interactive en
        """)
    
    print("="*60)

if __name__ == "__main__":
    main()
