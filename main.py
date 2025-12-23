"""
Main entry point for the welfare agent system
"""
import asyncio
import logging
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Import components
from src.agent.core import Agent
from src.agent.llm_provider import create_llm_provider
from src.voice.interface import create_voice_interface
from src.memory.manager import ConversationMemory
from src.tools.implementations import (
    SchemeDatabase, EligibilityChecker, 
    ApplicationTracker, UserProfileBuilder
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WelfareAgent:
    """Main welfare agent system"""
    
    def __init__(
        self,
        language: str = "te",
        llm_provider: str = "mock",
        voice_mode: str = "mock",
        api_key: Optional[str] = None
    ):
        """Initialize welfare agent
        
        Args:
            language: Language code (te, ta, mr, bn, or)
            llm_provider: LLM provider (mock, openai, gemini, local)
            voice_mode: Voice interface mode (mock, local, cloud)
            api_key: API key for LLM provider
        """
        self.language = language
        
        # Initialize components
        logger.info("Initializing welfare agent...")
        
        self.llm = create_llm_provider(llm_provider, api_key)
        self.voice = create_voice_interface(voice_mode)
        self.memory = ConversationMemory()
        
        # Initialize tools
        self.tools = {
            "scheme_database": SchemeDatabase(),
            "eligibility_checker": EligibilityChecker(),
            "application_tracker": ApplicationTracker(),
            "user_profile_builder": UserProfileBuilder()
        }
        
        # Initialize agent
        self.agent = Agent(
            llm_provider=self.llm,
            memory_manager=self.memory,
            voice_interface=self.voice,
            tools=self.tools
        )
        
        logger.info(f"Welfare agent initialized for language: {language}")

    async def process_user_input(self, user_input: Optional[str] = None) -> str:
        """Process user input through agent pipeline
        
        Args:
            user_input: Optional direct text input (for testing)
            
        Returns:
            Agent response
        """
        try:
            # Get user input
            if user_input is None:
                user_input = await self.agent.listen_and_process(self.language)
            else:
                self.memory.add_turn(role="user", content=user_input)
            
            if not user_input:
                return "I couldn't understand you. Please try again."
            
            logger.info(f"User: {user_input}")
            
            # Run agent loop
            response = await self.agent.run(user_input, self.language)
            
            logger.info(f"Agent: {response}")
            
            # Output response
            await self.voice.speak(response, self.language)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            error_response = f"Error: {str(e)}"
            return error_response

    async def interactive_session(self):
        """Run interactive text-based session"""
        logger.info("Starting interactive session...")
        print(f"\n=== Welfare Agent (Language: {self.language}) ===")
        print("Type 'quit' to exit, 'status' to see agent state, 'memory' to see conversation history\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == "quit":
                    print("Thank you for using the welfare agent!")
                    break
                elif user_input.lower() == "status":
                    print(f"Agent Status: {self.agent.get_state_info()}")
                    continue
                elif user_input.lower() == "memory":
                    history = self.memory.get_full_history()
                    for turn in history[-5:]:
                        print(f"{turn['role'].upper()}: {turn['content']}")
                    continue
                elif not user_input:
                    continue
                
                response = await self.process_user_input(user_input)
                print(f"Agent: {response}\n")
                
            except KeyboardInterrupt:
                print("\nSession interrupted.")
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"Error: {e}\n")

    async def voice_session(self):
        """Run interactive voice-based session (speak and listen)"""
        logger.info("Starting voice session...")
        print(f"\n=== 🎤 Welfare Agent Voice Mode (Language: {self.language}) ===")
        print("Speak to the agent! Say 'quit' or 'exit' to end the session.")
        print("Press Enter after speaking to allow the agent to respond.\n")
        
        # Step 1: Detect or select local language (ONLY ONCE at the very start)
        # Language detection happens ONLY ONCE - never again during the session
        selected_lang = self.language  # Use existing language as default
        
        # Only ask for language if we don't have a valid one set yet
        # (This entire block runs ONLY ONCE at session start - never when user says "no")
        if not hasattr(self, '_language_selected') or not self._language_selected:
            print("Let's detect your preferred language or choose one.")
            await self.voice.speak(
                "Please say a sentence in your preferred language. We will detect it.",
                "en"
            )
            detected_text = await self.voice.listen("auto")
            selected_lang = getattr(self.voice, "detected_language", None)
            # Maps for language names and codes
            code_to_name = {
                "en": "English",
                "te": "Telugu",
                "ta": "Tamil",
                "mr": "Marathi",
                "bn": "Bengali",
                "or": "Odia",
            }
            name_to_code = {k.lower(): v for v, k in code_to_name.items()}
            
            if not selected_lang:
                # Voice-only: Ask user to say language name again
                ask_lang_msg = {
                    "en": "I couldn't detect your language. Please say the language name: English, Telugu, Tamil, Marathi, Bengali, or Odia.",
                    "te": "నేను మీ భాషను గుర్తించలేకపోయాను. దయచేసి భాష పేరు చెప్పండి: English, Telugu, Tamil, Marathi, Bengali, లేదా Odia.",
                    "ta": "உங்கள் மொழியைக் கண்டறிய முடியவில்லை. தயவுசெய்து மொழி பெயரைச் சொல்லுங்கள்: English, Telugu, Tamil, Marathi, Bengali, அல்லது Odia.",
                    "mr": "मी तुमची भाषा ओळखू शकलो नाही. कृपया भाषेचे नाव सांगा: English, Telugu, Tamil, Marathi, Bengali, किंवा Odia.",
                    "bn": "আমি আপনার ভাষা শনাক্ত করতে পারিনি। অনুগ্রহ করে ভাষার নাম বলুন: English, Telugu, Tamil, Marathi, Bengali, বা Odia।",
                    "or": "ମୁଁ ଆପଣଙ୍କର ଭାଷା ଚିହ୍ନଟ କରିପାରିଲି ନାହିଁ। ଦୟାକରି ଭାଷାର ନାମ କହନ୍ତୁ: English, Telugu, Tamil, Marathi, Bengali, କିମ୍ବା Odia।"
                }
                await self.voice.speak(ask_lang_msg.get("en", ask_lang_msg["en"]), "en")
                lang_response = await self.voice.listen("auto")
                re_lang = getattr(self.voice, "detected_language", None)
                if re_lang and re_lang in code_to_name:
                    selected_lang = re_lang
                else:
                    # If still can't detect, try parsing the text response
                    lang_response_lower = (lang_response or "").lower()
                    for name, code in name_to_code.items():
                        if name in lang_response_lower or code in lang_response_lower:
                            selected_lang = code
                            break
                    if not selected_lang:
                        selected_lang = "en"  # Default to English
            
            # Confirm selection (voice-based with retry)
            lang_name = code_to_name.get(selected_lang, selected_lang)
            confirm_msg = {
                "en": f"Detected language: {lang_name}. Should I continue in this language? Please say yes or no.",
                "te": f"గుర్తించిన భాష: {lang_name}. ఈ భాషలో కొనసాగించవచ్చా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                "ta": f"கண்டறியப்பட்ட மொழி: {lang_name}. இதே மொழியில் தொடரலாமா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                "mr": f"ओळखलेली भाषा: {lang_name}. याच भाषेत पुढे जाऊ का? कृपया हो किंवा नाही बोला.",
                "bn": f"সনাক্ত ভাষা: {lang_name}. এই ভাষায় চলব? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                "or": f"ଚିହ୍ନଟ ଭାଷା: {lang_name}. ଏହି ଭାଷାରେ ଅଗ୍ରଗତି କରିବି କି? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
            }

            def _is_yes(text: str, lang: str) -> Optional[bool]:
                if not text:
                    return None
                t = text.strip().lower()
                yes_map = {
                    "en": ["yes", "y", "yeah", "yep", "ok", "okay", "enough", "done", "fine", "good"],
                    "te": ["అవును", "సరే", "చాలు", "ఓకే"],
                    "ta": ["ஆம்", "சரி", "போதும்"],
                    "mr": ["हो", "होय", "ठीक", "पुरे", "बरं"],
                    "bn": ["হ্যাঁ", "ঠিক আছে", "যথেষ্ট", "হ্যা"],
                    "or": ["ହଁ", "ଠିକ୍ ଅଛି", "ଯଥେଷ୍ଟ"]
                }
                no_map = {
                    "en": ["no", "n", "nope", "not"],
                    "te": ["కాదు", "వద్దు"],
                    "ta": ["இல்லை", "வேண்டாம்"],
                    "mr": ["नाही", "नको"],
                    "bn": ["না", "চাই না"],
                    "or": ["ନା", "ଦରକାର ନାହିଁ"]
                }
                if any(w in t for w in yes_map.get(lang, [])) or any(w in t for w in yes_map["en"]):
                    return True
                if any(w in t for w in no_map.get(lang, [])) or any(w in t for w in no_map["en"]):
                    return False
                return None

            # Get confirmation with voice-only retry
            lang_name = code_to_name.get(selected_lang, selected_lang)
            confirm_msg = {
                "en": f"Detected language: {lang_name}. Should I continue in this language? Please say yes or no.",
                "te": f"గుర్తించిన భాష: {lang_name}. ఈ భాషలో కొనసాగించవచ్చా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                "ta": f"கண்டறியப்பட்ட மொழி: {lang_name}. இதே மொழியில் தொடரலாமா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                "mr": f"ओळखलेली भाषा: {lang_name}. याच भाषेत पुढे जाऊ का? कृपया हो किंवा नाही बोला.",
                "bn": f"সনাক্ত ভাষা: {lang_name}. এই ভাষায় চলব? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                "or": f"ଚିହ୍ନଟ ଭାଷା: {lang_name}. ଏହି ଭାଷାରେ ଅଗ୍ରଗତି କରିବି କି? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
            }
            confirm_voice = ""
            decision = None
            for confirm_attempt in range(3):
                await self.voice.speak(confirm_msg.get(selected_lang, confirm_msg["en"]), selected_lang)
                confirm_voice = await self.voice.listen(selected_lang)
                decision = _is_yes(confirm_voice, selected_lang)
                if decision is not None:  # Got a valid yes/no response
                    break
                if confirm_attempt < 2:
                    repeat_confirm_msg = {
                        "en": "Sorry, I didn't understand. Please say yes or no.",
                        "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                        "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                        "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                        "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                        "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                    }
                    await self.voice.speak(repeat_confirm_msg.get(selected_lang, repeat_confirm_msg["en"]), selected_lang)
            
            if decision is False:
                # Ask user to say preferred language name and detect again
                reselect_msg = {
                    "en": "Please say the language name you prefer: English, Telugu, Tamil, Marathi, Bengali, or Odia.",
                    "te": "దయచేసి మీరు ఇష్టపడే భాషను చెప్పండి: English, Telugu, Tamil, Marathi, Bengali, లేదా Odia.",
                    "ta": "தயவுசெய்து நீங்கள் விரும்பும் மொழியைச் சொல்லுங்கள்: English, Telugu, Tamil, Marathi, Bengali, அல்லது Odia.",
                    "mr": "कृपया आपली पसंतीची भाषा बोला: English, Telugu, Tamil, Marathi, Bengali, किंवा Odia.",
                    "bn": "অনুগ্রহ করে আপনার পছন্দের ভাষার নাম বলুন: English, Telugu, Tamil, Marathi, Bengali, বা Odia।",
                    "or": "ଦୟାକରି ଆପଣଙ୍କ ପସନ୍ଦର ଭାଷା କହନ୍ତୁ: English, Telugu, Tamil, Marathi, Bengali, କିମ୍ବା Odia।"
                }
                await self.voice.speak(reselect_msg.get(selected_lang, reselect_msg["en"]), selected_lang)
                _ = await self.voice.listen("auto")
                re_lang = getattr(self.voice, "detected_language", None)
                if re_lang in code_to_name:
                    selected_lang = re_lang
                else:
                    # Voice-only: Ask to say language name again
                    ask_lang_again_msg = {
                        "en": "I couldn't understand. Please say the language name again: English, Telugu, Tamil, Marathi, Bengali, or Odia.",
                        "te": "నేను అర్థం చేసుకోలేదు. దయచేసి భాష పేరు మళ్లీ చెప్పండి: English, Telugu, Tamil, Marathi, Bengali, లేదా Odia.",
                        "ta": "எனக்கு புரியவில்லை. தயவுசெய்து மொழி பெயரை மீண்டும் சொல்லுங்கள்: English, Telugu, Tamil, Marathi, Bengali, அல்லது Odia.",
                        "mr": "मला समजले नाही. कृपया भाषेचे नाव पुन्हा सांगा: English, Telugu, Tamil, Marathi, Bengali, किंवा Odia.",
                        "bn": "আমি বুঝতে পারিনি। অনুগ্রহ করে ভাষার নাম আবার বলুন: English, Telugu, Tamil, Marathi, Bengali, বা Odia।",
                        "or": "ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ଭାଷାର ନାମ ପୁନର୍ବାର କହନ୍ତୁ: English, Telugu, Tamil, Marathi, Bengali, କିମ୍ବା Odia।"
                    }
                    await self.voice.speak(ask_lang_again_msg.get(selected_lang, ask_lang_again_msg["en"]), selected_lang)
                    lang_response = await self.voice.listen("auto")
                    re_lang2 = getattr(self.voice, "detected_language", None)
                    if re_lang2 and re_lang2 in code_to_name:
                        selected_lang = re_lang2
                    else:
                        # Try parsing text
                        lang_response_lower = (lang_response or "").lower()
                        for name, code in name_to_code.items():
                            if name in lang_response_lower or code in lang_response_lower:
                                selected_lang = code
                                break
                        if not selected_lang:
                            selected_lang = "en"  # Default to English
            elif decision is None:
                # If unclear, default to current selection
                pass
            
            self.language = selected_lang
            self._language_selected = True  # Mark language as selected
        
        # Language is now set for the entire session - will never be asked again
        
        # Welcome message
        welcome_msg = {
            "te": "నమస్కారం! నేను మీ సహాయ కార్యకర్త. మీకు ఎలా సహాయం చేయగలను?",
            "ta": "வணக்கம்! நான் உங்கள் நல உதவியாளர். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "mr": "नमस्कार! मी तुमचा कल्याण सहाय्यक आहे. मी तुम्हाला कशी मदत करू शकतो?",
            "bn": "নমস্কার! আমি আপনার কল্যাণ সহায়ক। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
            "or": "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କର କଲ୍ୟାଣ ସହାୟକ | ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?",
            "en": "Hello! I am your welfare assistant. How can I help you today?"
        }
        await self.voice.speak(welcome_msg.get(self.language, welcome_msg["en"]), self.language)
        
        # Helper function to get voice input with retry
        async def get_voice_input(prompt_msg: Dict[str, str], max_retries: int = 3) -> str:
            """Get voice input, asking user to repeat if not understood"""
            repeat_msg = {
                "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి మళ్లీ చెప్పండి.",
                "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து மீண்டும் சொல்லுங்கள்.",
                "mr": "माफ करा, मला समजले नाही. कृपया पुन्हा बोला.",
                "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে আবার বলুন।",
                "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ପୁନର୍ବାର କହନ୍ତୁ।",
                "en": "Sorry, I didn't understand. Please say again."
            }
            
            for attempt in range(max_retries):
                await self.voice.speak(prompt_msg.get(self.language, prompt_msg["en"]), self.language)
                user_input = await self.voice.listen(self.language)
                
                if user_input and user_input.strip():
                    return user_input.strip()
                
                # Ask to repeat if empty
                if attempt < max_retries - 1:
                    await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
            
            # Final attempt failed, return empty (caller can handle)
            return ""
        
        # Ask what they need from the agent (voice only, no text fallback)
        ask_need_msg = {
            "te": "మీకు ఏమి కావాలి? దయచేసి మీ అవసరాన్ని చెప్పండి.",
            "ta": "உங்களுக்கு என்ன தேவை? தயவுசெய்து உங்கள் தேவையைக் கூறுங்கள்.",
            "mr": "तुम्हाला काय हवे आहे? कृपया तुमची गरज सांगा.",
            "bn": "আপনার কী প্রয়োজন? অনুগ্রহ করে আপনার প্রয়োজন বলুন।",
            "or": "ଆପଣଙ୍କୁ କଣ ଦରକାର? ଦୟାକରି ଆପଣଙ୍କର ଆବଶ୍ୟକତା କହନ୍ତୁ।",
            "en": "What do you need? Please tell me your requirement."
        }
        user_need = await get_voice_input(ask_need_msg)
        
        # Store the user's need in memory
        if user_need:
            self.memory.add_turn(role="user", content=user_need)
        
        # Helper function to check yes/no responses
        def _is_yes(text: str, lang: str) -> Optional[bool]:
            if not text:
                return None
            t = text.strip().lower()
            yes_map = {
                "en": ["yes", "y", "yeah", "yep", "ok", "okay", "enough", "done", "fine", "good"],
                "te": ["అవును", "సరే", "చాలు", "ఓకే"],
                "ta": ["ஆம்", "சரி", "போதும்"],
                "mr": ["हो", "होय", "ठीक", "पुरे", "बरं"],
                "bn": ["হ্যাঁ", "ঠিক আছে", "যথেষ্ট", "হ্যা"],
                "or": ["ହଁ", "ଠିକ୍ ଅଛି", "ଯଥେଷ୍ଟ"]
            }
            no_map = {
                "en": ["no", "n", "nope", "not"],
                "te": ["కాదు", "వద్దు"],
                "ta": ["இல்லை", "வேண்டாம்"],
                "mr": ["नाही", "नको"],
                "bn": ["না", "চাই না"],
                "or": ["ନା", "ଦରକାର ନାହିଁ"]
            }
            if any(w in t for w in yes_map.get(lang, [])) or any(w in t for w in yes_map["en"]):
                return True
            if any(w in t for w in no_map.get(lang, [])) or any(w in t for w in no_map["en"]):
                return False
            return None
        
        # Helper function to gather profile and show eligible schemes
        async def gather_profile_and_show_schemes():
            """Gather user profile and show eligible schemes"""
            # Step 2: Gather basic profile to compute available schemes
            ask_age = {
                "en": "Please tell me your age.",
                "te": "దయచేసి మీ వయస్సు చెప్పండి.",
                "ta": "தயவு செய்து உங்கள் வயதை கூறுங்கள்.",
                "mr": "कृपया तुमचे वय सांगा.",
                "bn": "অনুগ্রহ করে আপনার বয়স বলুন।",
                "or": "ଦୟାକରି ଆପଣଙ୍କ ବୟସ୍ କହନ୍ତୁ।"
            }
            ask_income = {
                "en": "Please tell me your approximate annual income.",
                "te": "మీ వార్షిక ఆదాయం సుమారు ఎంత?",
                "ta": "உங்கள் வருடாந்திர வருமானம் எவ்வளவு?",
                "mr": "तुमचे वार्षिक उत्पन्न किती आहे?",
                "bn": "আপনার বার্ষিক আয় কত?",
                "or": "ଆପଣଙ୍କ ବାର୍ଷିକ ଆୟ କେତେ?"
            }
            ask_category = {
                "en": "What is your social category? (SC/ST/OBC/General)",
                "te": "మీ సామాజిక వర్గం ఏమిటి? (SC/ST/OBC/General)",
                "ta": "உங்கள் சமூக வகுப்பு என்ன? (SC/ST/OBC/General)",
                "mr": "आपली सामाजिक श्रेणी काय आहे? (SC/ST/OBC/General)",
                "bn": "আপনার সামাজিক শ্রেণী কী? (SC/ST/OBC/General)",
                "or": "ଆପଣଙ୍କ ସମାଜିକ ଶ୍ରେଣୀ କୋଣସି? (SC/ST/OBC/General)"
            }
            
            # Ask and listen (voice only - ask to repeat if not understood)
            age_text = await get_voice_input(ask_age)
            income_text = await get_voice_input(ask_income)
            category_text = await get_voice_input(ask_category)
            
            # Parse basic values
            import re
            def parse_number(text: str, default: int) -> int:
                m = re.findall(r"\d+", text or "")
                return int(m[0]) if m else default
            age_val = parse_number(age_text, 30)
            income_val = parse_number(income_text, 0)
            # Parse basic values
            import re
            def parse_number(text: str, default: int) -> int:
                m = re.findall(r"\d+", text or "")
                return int(m[0]) if m else default
            age_val = parse_number(age_text, 30)
            income_val = parse_number(income_text, 0)
            category_val = (category_text or "General").upper()
            if category_val not in ["SC", "ST", "OBC", "GENERAL"]:
                category_val = "GENERAL"
            
            profile_updates = {
                "age": age_val,
                "annual_income": income_val,
                "category": "General" if category_val == "GENERAL" else category_val
            }
            self.memory.update_user_profile(profile_updates)
            
            # Compute eligible schemes and speak them
            try:
                eligibility = await self.tools["eligibility_checker"].execute({
                    "user_profile": self.memory.user_profile
                })
                schemes_db = await self.tools["scheme_database"].execute({
                    "language": self.language
                })
                eligible_names = set([name.lower() for name in eligibility.get("eligible_schemes", [])])
                available = schemes_db.get("schemes", [])
                matched = []
                for s in available:
                    eng = (s.get("english_name") or s.get("name") or "").lower()
                    name = (s.get("name") or "").lower()
                    if any(k in eng or k in name for k in eligible_names):
                        matched.append(s)
                
                if matched:
                    # Announce all eligible schemes
                    lines = [f"• {s.get('name')} ({s.get('english_name')})" for s in matched]
                    speak_text = {
                    "en": "Based on your details, you may be eligible for: \n" + "\n".join(lines),
                    "te": "మీ వివరాల ప్రకారం, మీరు అర్హత కలిగిన స్కీమ్‌లు: \n" + "\n".join(lines),
                    "ta": "உங்கள் விவரங்களைப் பொறுத்து, நீங்கள் தகுதியான திட்டங்கள்: \n" + "\n".join(lines),
                    "mr": "तुमच्या माहितीनुसार, तुम्ही पात्र असू शकता: \n" + "\n".join(lines),
                    "bn": "আপনার তথ্য অনুযায়ী, আপনি যে স্কিমগুলির জন্য যোগ্য হতে পারেন: \n" + "\n".join(lines),
                        "or": "ଆପଣଙ୍କ ତଥ୍ୟ ଅନୁସାରେ, ଆପଣ ଯୋଗ୍ୟ ହୋଇପାରନ୍ତି: \n" + "\n".join(lines)
                    }
                    await self.voice.speak(speak_text.get(self.language, speak_text["en"]), self.language)
                    
                    # Ask if they need more information about the schemes
                    ask_more_info_msg = {
                        "en": "Do you need any more information about these schemes, such as required documents, where to apply, or the application process? Please say yes or no.",
                        "te": "ఈ స్కీమ్‌ల గురించి మీకు మరింత సమాచారం అవసరమా? ఉదాహరణకు, అవసరమైన పత్రాలు, ఎక్కడ దరఖాస్తు చేయాలి, లేదా దరఖాస్తు ప్రక్రియ? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                        "ta": "இந்த திட்டங்கள் பற்றி உங்களுக்கு மேலும் தகவல் தேவையா? எடுத்துக்காட்டாக, தேவையான ஆவணங்கள், எங்கு விண்ணப்பிக்க வேண்டும், அல்லது விண்ணப்ப செயல்முறை? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                        "mr": "या योजनांबद्दल तुम्हाला आणखी माहिती हवी आहे का? उदाहरणार्थ, आवश्यक कागदपत्रे, कोठे अर्ज करायचा, किंवा अर्ज प्रक्रिया? कृपया हो किंवा नाही बोला.",
                        "bn": "এই স্কিমগুলির সম্পর্কে আপনার আরও তথ্য প্রয়োজন? উদাহরণস্বরূপ, প্রয়োজনীয় নথি, কোথায় আবেদন করবেন, বা আবেদনের প্রক্রিয়া? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                        "or": "ଏହି ଯୋଜନାଗୁଡ଼ିକ ବିଷୟରେ ଆପଣଙ୍କର ଆହୁରି ସୂଚନା ଦରକାର କି? ଉଦାହରଣ ସ୍ୱରୂପ, ଆବଶ୍ୟକ ଦସ୍ତାବେଜ, କେଉଁଠାରେ ଆବେଦନ କରିବେ, କିମ୍ବା ଆବେଦନ ପ୍ରକ୍ରିୟା? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                    }
                    await self.voice.speak(ask_more_info_msg.get(self.language, ask_more_info_msg["en"]), self.language)
                    
                    # Get user response with retry
                    need_more_info = None
                    for info_attempt in range(3):
                        more_info_voice = await self.voice.listen(self.language)
                        try:
                            need_more_info = _is_yes(more_info_voice, self.language)
                            if need_more_info is not None:
                                break
                        except Exception:
                            pass
                        if info_attempt < 2:
                            repeat_msg = {
                                "en": "Sorry, I didn't understand. Please say yes or no.",
                                "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                                "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                            }
                            await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                    
                    # Only provide application details if user says yes
                    if need_more_info is True:
                        # Provide guidance: documents, where to apply, steps for each scheme
                        for scheme_idx, s in enumerate(matched):
                            doc_list = s.get("documents", [])
                            where = s.get("where_to_apply")
                            steps = s.get("apply_steps", [])
                            guidance_lines = []
                            if doc_list:
                                guidance_lines.append(({
                                "en": "Required documents:",
                                "te": "అవసరమైన పత్రాలు:",
                                "ta": "தேவையான ஆவணங்கள்:",
                                "mr": "आवश्यक कागदपत्रे:",
                                "bn": "প্রয়োজনীয় নথি:",
                                "or": "ଆବଶ୍ୟକ ଦସ୍ତାବେଜ:",
                                }).get(self.language, "Required documents:") + " " + ", ".join(doc_list))
                            if where:
                                guidance_lines.append(({
                                "en": "Where to apply:",
                                "te": "ఎక్కడ దరఖాస్తు చేయాలి:",
                                "ta": "எங்கு விண்ணப்பிக்க வேண்டும்:",
                                "mr": "कोठे अर्ज करायचा:",
                                "bn": "কোথায় আবেদন করবেন:",
                                "or": "କେଉଁଠାରେ ଆବେଦନ କରିବେ:",
                                }).get(self.language, "Where to apply:") + f" {where}")
                            if steps:
                                numbered = [f"{i+1}. {st}" for i, st in enumerate(steps)]
                                guidance_lines.append(({
                                "en": "Steps to apply:",
                                "te": "అప్లై చేసే దశలు:",
                                "ta": "விண்ணப்பிக்கும் படிகள்:",
                                "mr": "अर्ज करण्याच्या पायऱ्या:",
                                "bn": "আবেদনের ধাপসমূহ:",
                                "or": "ଆବେଦନ ପଦକ୍ରମ:",
                                }).get(self.language, "Steps to apply:") + " \n" + "\n".join(numbered))
                            if guidance_lines:
                                await self.voice.speak(({
                                "en": f"For {s.get('english_name')}: \n" + "\n".join(guidance_lines),
                                "te": f"{s.get('name')} కోసం: \n" + "\n".join(guidance_lines),
                                "ta": f"{s.get('name')} க்காக: \n" + "\n".join(guidance_lines),
                                "mr": f"{s.get('name')} साठी: \n" + "\n".join(guidance_lines),
                                "bn": f"{s.get('name')} এর জন্য: \n" + "\n".join(guidance_lines),
                                "or": f"{s.get('name')} ପାଇଁ: \n" + "\n".join(guidance_lines),
                                }).get(self.language, f"For {s.get('english_name')}: \n" + "\n".join(guidance_lines)), self.language)
                            
                            # After showing steps, ask if satisfied and want to apply
                            ask_satisfied_msg = {
                                "en": "Are you satisfied with this information? Do you want to apply for this scheme? Please say yes or no.",
                                "te": "మీరు ఈ సమాచారంతో సంతృప్తి చెందారా? మీరు ఈ స్కీమ్‌కు దరఖాస్తు చేయాలనుకుంటున్నారా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                "ta": "இந்த தகவலில் நீங்கள் திருப்தியா? இந்த திட்டத்திற்கு விண்ணப்பிக்க விரும்புகிறீர்களா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                "mr": "तुम्ही या माहितीने समाधानी आहात का? तुम्ही या योजनेसाठी अर्ज करू इच्छिता का? कृपया हो किंवा नाही बोला.",
                                "bn": "আপনি এই তথ্যে সন্তুষ্ট? আপনি এই স্কিমের জন্য আবেদন করতে চান? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                "or": "ଆପଣ ଏହି ସୂଚନାରେ ସନ୍ତୁଷ୍ଟ କି? ଆପଣ ଏହି ଯୋଜନା ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି କି? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                            }
                            await self.voice.speak(ask_satisfied_msg.get(self.language, ask_satisfied_msg["en"]), self.language)
                            
                            # Get response with retry
                            want_to_apply = None
                            for apply_attempt in range(3):
                                apply_voice = await self.voice.listen(self.language)
                                try:
                                    want_to_apply = _is_yes(apply_voice, self.language)
                                    if want_to_apply is not None:
                                        break
                                except Exception:
                                    pass
                                if apply_attempt < 2:
                                    repeat_msg = {
                                        "en": "Sorry, I didn't understand. Please say yes or no.",
                                        "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                        "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                        "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                                        "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                        "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                                    }
                                    await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                            
                            # If user wants to apply
                            if want_to_apply is True:
                                # Apply for the scheme
                                scheme_name = s.get('english_name') or s.get('name')
                                try:
                                    app_result = await self.tools["application_tracker"].execute({
                                        "action": "create",
                                        "user_id": "default",
                                        "scheme_name": scheme_name
                                    })
                                    # Say successfully applied
                                    applied_msg = {
                                        "en": f"Your application for {scheme_name} has been successfully submitted. Your application ID is {app_result.get('application_id', 'pending')}.",
                                        "te": f"{scheme_name} కోసం మీ దరఖాస్తు విజయవంతంగా సమర్పించబడింది. మీ దరఖాస్తు ID {app_result.get('application_id', 'pending')}.",
                                        "ta": f"{scheme_name} க்கான உங்கள் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது. உங்கள் விண்ணப்ப ID {app_result.get('application_id', 'pending')}.",
                                        "mr": f"{scheme_name} साठी तुमची अर्ज यशस्वीपणे सबमिट केली आहे. तुमचा अर्ज ID {app_result.get('application_id', 'pending')}.",
                                        "bn": f"{scheme_name} এর জন্য আপনার আবেদন সফলভাবে জমা দেওয়া হয়েছে। আপনার আবেদন ID {app_result.get('application_id', 'pending')}.",
                                        "or": f"{scheme_name} ପାଇଁ ଆପଣଙ୍କର ଆବେଦନ ସଫଳତାପୂର୍ବକ ଦାଖଲ କରାଯାଇଛି। ଆପଣଙ୍କର ଆବେଦନ ID {app_result.get('application_id', 'pending')}।"
                                    }
                                    await self.voice.speak(applied_msg.get(self.language, applied_msg["en"]), self.language)
                                    
                                    # End with greetings
                                    farewell = {
                                        "te": "ధన్యవాదాలు! ఏదైనా సహాయం అవసరమైతే మళ్లీ సందర్శించండి. మీకు మంచి రోజు కలగాలి!",
                                        "ta": "நன்றி! எந்த உதவி தேவைப்பட்டால் மீண்டும் வாருங்கள். உங்களுக்கு நல்ல நாள் வேண்டும்!",
                                        "mr": "धन्यवाद! जर काही मदत हवी असेल तर पुन्हा भेट द्या. तुमचा दिवस चांगला जावो!",
                                        "bn": "ধন্যবাদ! আর কোন সাহায্যের প্রয়োজন হলে আবার আসুন। আপনার ভাল দিন হোক!",
                                        "or": "ଧନ୍ୟବାଦ! ଯଦି ଆହୁରି ସାହାଯ୍ୟ ଦରକାର ତେବେ ପୁନର୍ବାର ଆସନ୍ତୁ। ଆପଣଙ୍କର ଭଲ ଦିନ ହେଉ!",
                                        "en": "Thank you! Visit again if any help is needed. Have a great day!"
                                    }
                                    await self.voice.speak(farewell.get(self.language, farewell["en"]), self.language)
                                    return True  # Signal that application was successful, exit flow
                                except Exception as e:
                                    logger.error(f"Application error: {e}")
                            
                            # If user says no, try next scheme
                            elif want_to_apply is False:
                                # Check if there are more schemes to show
                                if scheme_idx < len(matched) - 1:
                                    # Show next scheme
                                    continue
                                else:
                                    # No more eligible schemes, show available schemes
                                    no_more_eligible_msg = {
                                        "en": "There are no more eligible schemes available. However, here are the schemes that are available:",
                                        "te": "ఇక మరిన్ని అర్హత కలిగిన స్కీమ్‌లు లేవు. అయినప్పటికీ, ఇక్కడ అందుబాటులో ఉన్న స్కీమ్‌లు ఇవి:",
                                        "ta": "இனி தகுதியான திட்டங்கள் இல்லை. இருப்பினும், கிடைக்கக்கூடிய திட்டங்கள் இங்கே:",
                                        "mr": "आणखी पात्र योजना उपलब्ध नाहीत. तथापि, येथे उपलब्ध योजना आहेत:",
                                        "bn": "আর কোন যোগ্য স্কিম নেই। তবে, এখানে উপলব্ধ স্কিমগুলি রয়েছে:",
                                        "or": "ଆହୁରି ଯୋଗ୍ୟ ଯୋଜନା ଉପଲବ୍ଧ ନାହିଁ। ଯଦିଓ, ଏଠାରେ ଉପଲବ୍ଧ ଯୋଜନାଗୁଡ଼ିକ ହେଉଛି:"
                                    }
                                    await self.voice.speak(no_more_eligible_msg.get(self.language, no_more_eligible_msg["en"]), self.language)
                                    
                                    # Show all available schemes
                                    all_schemes = schemes_db.get("schemes", [])
                                    if all_schemes:
                                        all_lines = [f"• {s.get('name')} ({s.get('english_name')})" for s in all_schemes[:5]]  # Limit to 5
                                        all_schemes_text = {
                                            "en": "\n".join(all_lines),
                                            "te": "\n".join(all_lines),
                                            "ta": "\n".join(all_lines),
                                            "mr": "\n".join(all_lines),
                                            "bn": "\n".join(all_lines),
                                            "or": "\n".join(all_lines)
                                        }
                                        await self.voice.speak(all_schemes_text.get(self.language, all_schemes_text["en"]), self.language)
                                        
                                        # Ask if okay with available schemes
                                        ask_okay_available_msg = {
                                            "en": "Are you okay with any of these available schemes? If yes, please tell me which one you want to apply for.",
                                            "te": "మీరు ఈ అందుబాటులో ఉన్న స్కీమ్‌లలో దేనితోనైనా సరిపోతారా? అవును అయితే, దయచేసి మీరు దరఖాస్తు చేయాలనుకునేది ఏది అని చెప్పండి.",
                                            "ta": "இந்த கிடைக்கக்கூடிய திட்டங்களில் ஏதேனும் உங்களுக்கு பொருந்துமா? ஆம் என்றால், தயவுசெய்து நீங்கள் விண்ணப்பிக்க விரும்பும் திட்டத்தைச் சொல்லுங்கள்.",
                                            "mr": "तुम्ही या उपलब्ध योजनांपैकी कोणत्याही बरोबर सहमत आहात का? होय असल्यास, कृपया तुम्हाला कोणत्या योजनेसाठी अर्ज करायचा आहे ते सांगा.",
                                            "bn": "এই উপলব্ধ স্কিমগুলির মধ্যে কোনও একটি আপনার জন্য ঠিক আছে? হ্যাঁ হলে, অনুগ্রহ করে কোনটির জন্য আবেদন করতে চান তা বলুন।",
                                            "or": "ଏହି ଉପଲବ୍ଧ ଯୋଜନାଗୁଡ଼ିକ ମଧ୍ୟରୁ କୌଣସି ଗୋଟିଏ ଆପଣଙ୍କ ପାଇଁ ଠିକ୍ ଅଛି କି? ହଁ ହେଲେ, ଦୟାକରି ଆପଣ କେଉଁଟି ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି ତାହା କହନ୍ତୁ।"
                                        }
                                        await self.voice.speak(ask_okay_available_msg.get(self.language, ask_okay_available_msg["en"]), self.language)
                                        
                                        # Get user's choice
                                        choice_voice = await self.voice.listen(self.language)
                                        if choice_voice:
                                            # Try to match the scheme name
                                            choice_lower = choice_voice.lower()
                                            for avail_scheme in all_schemes:
                                                if (avail_scheme.get('name', '').lower() in choice_lower or 
                                                    avail_scheme.get('english_name', '').lower() in choice_lower):
                                                    # Apply for this scheme
                                                    chosen_scheme_name = avail_scheme.get('english_name') or avail_scheme.get('name')
                                                    try:
                                                        app_result = await self.tools["application_tracker"].execute({
                                                            "action": "create",
                                                            "user_id": "default",
                                                            "scheme_name": chosen_scheme_name
                                                        })
                                                        applied_msg = {
                                                            "en": f"Your application for {chosen_scheme_name} has been successfully submitted. Your application ID is {app_result.get('application_id', 'pending')}.",
                                                            "te": f"{chosen_scheme_name} కోసం మీ దరఖాస్తు విజయవంతంగా సమర్పించబడింది. మీ దరఖాస్తు ID {app_result.get('application_id', 'pending')}.",
                                                            "ta": f"{chosen_scheme_name} க்கான உங்கள் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது. உங்கள் விண்ணப்ப ID {app_result.get('application_id', 'pending')}.",
                                                            "mr": f"{chosen_scheme_name} साठी तुमची अर्ज यशस्वीपणे सबमिट केली आहे. तुमचा अर्ज ID {app_result.get('application_id', 'pending')}.",
                                                            "bn": f"{chosen_scheme_name} এর জন্য আপনার আবেদন সফলভাবে জমা দেওয়া হয়েছে। আপনার আবেদন ID {app_result.get('application_id', 'pending')}.",
                                                            "or": f"{chosen_scheme_name} ପାଇଁ ଆପଣଙ୍କର ଆବେଦନ ସଫଳତାପୂର୍ବକ ଦାଖଲ କରାଯାଇଛି। ଆପଣଙ୍କର ଆବେଦନ ID {app_result.get('application_id', 'pending')}।"
                                                        }
                                                        await self.voice.speak(applied_msg.get(self.language, applied_msg["en"]), self.language)
                                                        
                                                        # End with greetings
                                                        farewell = {
                                                            "te": "ధన్యవాదాలు! ఏదైనా సహాయం అవసరమైతే మళ్లీ సందర్శించండి. మీకు మంచి రోజు కలగాలి!",
                                                            "ta": "நன்றி! எந்த உதவி தேவைப்பட்டால் மீண்டும் வாருங்கள். உங்களுக்கு நல்ல நாள் வேண்டும்!",
                                                            "mr": "धन्यवाद! जर काही मदत हवी असेल तर पुन्हा भेट द्या. तुमचा दिवस चांगला जावो!",
                                                            "bn": "ধন্যবাদ! আর কোন সাহায্যের প্রয়োজন হলে আবার আসুন। আপনার ভাল দিন হোক!",
                                                            "or": "ଧନ୍ୟବାଦ! ଯଦି ଆହୁରି ସାହାଯ୍ୟ ଦରକାର ତେବେ ପୁନର୍ବାର ଆସନ୍ତୁ। ଆପଣଙ୍କର ଭଲ ଦିନ ହେଉ!",
                                                            "en": "Thank you! Visit again if any help is needed. Have a great day!"
                                                        }
                                                        await self.voice.speak(farewell.get(self.language, farewell["en"]), self.language)
                                                        return True  # Exit flow - application successful
                                                    except Exception as e:
                                                        logger.error(f"Application error: {e}")
                                                        break
                                    break  # Exit scheme loop
                    
                    # If user didn't want more info, ask if they want to apply at all
                    if need_more_info is False:
                        if matched:
                            # Ask if they want to apply for any scheme
                            ask_apply_general_msg = {
                                "en": "Would you like to apply for any of these eligible schemes? Please say yes or no.",
                                "te": "మీరు ఈ అర్హత కలిగిన స్కీమ్‌లలో దేనికైనా దరఖాస్తు చేయాలనుకుంటున్నారా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                "ta": "இந்த தகுதியான திட்டங்களில் ஏதேனும் ஒன்றிற்கு விண்ணப்பிக்க விரும்புகிறீர்களா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                "mr": "तुम्ही या पात्र योजनांपैकी कोणत्याही साठी अर्ज करू इच्छिता का? कृपया हो किंवा नाही बोला.",
                                "bn": "আপনি এই যোগ্য স্কিমগুলির মধ্যে কোনও একটি জন্য আবেদন করতে চান? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                "or": "ଆପଣ ଏହି ଯୋଗ୍ୟ ଯୋଜନାଗୁଡ଼ିକ ମଧ୍ୟରୁ କୌଣସିଟି ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି କି? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                            }
                            await self.voice.speak(ask_apply_general_msg.get(self.language, ask_apply_general_msg["en"]), self.language)
                            
                            apply_general = None
                            for general_attempt in range(3):
                                general_voice = await self.voice.listen(self.language)
                                try:
                                    apply_general = _is_yes(general_voice, self.language)
                                    if apply_general is not None:
                                        break
                                except Exception:
                                    pass
                                if general_attempt < 2:
                                    repeat_msg = {
                                        "en": "Sorry, I didn't understand. Please say yes or no.",
                                        "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                        "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                        "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                                        "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                        "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                                    }
                                    await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                            
                            # If user says yes, let them choose which scheme to apply for
                            if apply_general is True:
                                # Show all eligible schemes again and ask which one
                                all_eligible_lines = [f"• {s.get('name')} ({s.get('english_name')})" for s in matched]
                                show_all_eligible_msg = {
                                    "en": "Here are all the schemes you are eligible for: \n" + "\n".join(all_eligible_lines) + "\n\nPlease tell me which scheme you would like to apply for.",
                                    "te": "మీరు అర్హత కలిగిన అన్ని స్కీమ్‌లు ఇవి: \n" + "\n".join(all_eligible_lines) + "\n\nదయచేసి మీరు దరఖాస్తు చేయాలనుకునే స్కీమ్‌ను చెప్పండి.",
                                    "ta": "நீங்கள் தகுதியான அனைத்து திட்டங்கள் இவை: \n" + "\n".join(all_eligible_lines) + "\n\nதயவுசெய்து எந்த திட்டத்திற்கு விண்ணப்பிக்க விரும்புகிறீர்கள் என்று சொல்லுங்கள்.",
                                    "mr": "तुम्ही पात्र असलेल्या सर्व योजना येथे आहेत: \n" + "\n".join(all_eligible_lines) + "\n\nकृपया तुम्हाला कोणत्या योजनेसाठी अर्ज करायचा आहे ते सांगा.",
                                    "bn": "আপনি যোগ্য সমস্ত স্কিমগুলি এখানে রয়েছে: \n" + "\n".join(all_eligible_lines) + "\n\nঅনুগ্রহ করে কোন স্কিমের জন্য আবেদন করতে চান তা বলুন।",
                                    "or": "ଆପଣ ଯୋଗ୍ୟ ସମସ୍ତ ଯୋଜନାଗୁଡ଼ିକ ଏଠାରେ ଅଛନ୍ତି: \n" + "\n".join(all_eligible_lines) + "\n\nଦୟାକରି ଆପଣ କେଉଁଟି ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି ତାହା କହନ୍ତୁ।"
                                }
                                await self.voice.speak(show_all_eligible_msg.get(self.language, show_all_eligible_msg["en"]), self.language)
                                
                                # Get user's choice
                                choice_voice = await self.voice.listen(self.language)
                                if choice_voice and choice_voice.strip():
                                    choice_lower = choice_voice.lower().strip()
                                    # Find the scheme that matches - use word boundaries for better matching
                                    matched_scheme = None
                                    for scheme in matched:
                                        scheme_name_lower = scheme.get('name', '').lower().strip()
                                        scheme_english_lower = scheme.get('english_name', '').lower().strip()
                                        # Check if the scheme name or english name is mentioned as a complete phrase
                                        # Use word boundary checking to avoid partial matches
                                        if (scheme_name_lower and scheme_name_lower in choice_lower) or \
                                           (scheme_english_lower and scheme_english_lower in choice_lower):
                                            # Additional check: make sure it's not just a partial word match
                                            # Extract key words from scheme names for better matching
                                            scheme_keywords = set(scheme_english_lower.split() + scheme_name_lower.split())
                                            user_words = set(choice_lower.split())
                                            # Check if at least 2 key words match (to avoid false positives)
                                            if len(scheme_keywords.intersection(user_words)) >= 2:
                                                matched_scheme = scheme
                                                break
                                    
                                    # Only proceed if we found a valid scheme match
                                    if matched_scheme:
                                        # Confirm before applying
                                        chosen_scheme_name = matched_scheme.get('english_name') or matched_scheme.get('name')
                                        confirm_apply_msg = {
                                            "en": f"Did you say you want to apply for {chosen_scheme_name}? Please say yes or no.",
                                            "te": f"మీరు {chosen_scheme_name} కోసం దరఖాస్తు చేయాలని చెప్పారా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                            "ta": f"நீங்கள் {chosen_scheme_name} க்கு விண்ணப்பிக்க விரும்புகிறீர்கள் என்று சொன்னீர்களா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                            "mr": f"तुम्ही {chosen_scheme_name} साठी अर्ज करू इच्छिता असे म्हटले? कृपया हो किंवा नाही बोला.",
                                            "bn": f"আপনি কি {chosen_scheme_name} এর জন্য আবেদন করতে চান? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                            "or": f"ଆପଣ {chosen_scheme_name} ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି ବୋଲି କହିଲେ? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                                        }
                                        await self.voice.speak(confirm_apply_msg.get(self.language, confirm_apply_msg["en"]), self.language)
                                        
                                        # Get confirmation
                                        confirm_choice = None
                                        for confirm_attempt in range(3):
                                            confirm_voice = await self.voice.listen(self.language)
                                            try:
                                                confirm_choice = _is_yes(confirm_voice, self.language)
                                                if confirm_choice is not None:
                                                    break
                                            except Exception:
                                                pass
                                            if confirm_attempt < 2:
                                                repeat_msg = {
                                                    "en": "Sorry, I didn't understand. Please say yes or no.",
                                                    "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                                    "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                                    "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                                                    "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                                    "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                                                }
                                                await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                                        
                                        # Only apply if user confirmed yes
                                        if confirm_choice is True:
                                            try:
                                                app_result = await self.tools["application_tracker"].execute({
                                                    "action": "create",
                                                    "user_id": "default",
                                                    "scheme_name": chosen_scheme_name
                                                })
                                                applied_msg = {
                                                    "en": f"Your application for {chosen_scheme_name} has been successfully submitted. Your application ID is {app_result.get('application_id', 'pending')}.",
                                                    "te": f"{chosen_scheme_name} కోసం మీ దరఖాస్తు విజయవంతంగా సమర్పించబడింది. మీ దరఖాస్తు ID {app_result.get('application_id', 'pending')}.",
                                                    "ta": f"{chosen_scheme_name} க்கான உங்கள் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது. உங்கள் விண்ணப்ப ID {app_result.get('application_id', 'pending')}.",
                                                    "mr": f"{chosen_scheme_name} साठी तुमची अर्ज यशस्वीपणे सबमिट केली आहे. तुमचा अर्ज ID {app_result.get('application_id', 'pending')}.",
                                                    "bn": f"{chosen_scheme_name} এর জন্য আপনার আবেদন সফলভাবে জমা দেওয়া হয়েছে। আপনার আবেদন ID {app_result.get('application_id', 'pending')}.",
                                                    "or": f"{chosen_scheme_name} ପାଇଁ ଆପଣଙ୍କର ଆବେଦନ ସଫଳତାପୂର୍ବକ ଦାଖଲ କରାଯାଇଛି। ଆପଣଙ୍କର ଆବେଦନ ID {app_result.get('application_id', 'pending')}।"
                                                }
                                                await self.voice.speak(applied_msg.get(self.language, applied_msg["en"]), self.language)
                                                
                                                # End with greetings
                                                farewell = {
                                                    "te": "ధన్యవాదాలు! ఏదైనా సహాయం అవసరమైతే మళ్లీ సందర్శించండి. మీకు మంచి రోజు కలగాలి!",
                                                    "ta": "நன்றி! எந்த உதவி தேவைப்பட்டால் மீண்டும் வாருங்கள். உங்களுக்கு நல்ல நாள் வேண்டும்!",
                                                    "mr": "धन्यवाद! जर काही मदत हवी असेल तर पुन्हा भेट द्या. तुमचा दिवस चांगला जावो!",
                                                    "bn": "ধন্যবাদ! আর কোন সাহায্যের প্রয়োজন হলে আবার আসুন। আপনার ভাল দিন হোক!",
                                                    "or": "ଧନ୍ୟବାଦ! ଯଦି ଆହୁରି ସାହାଯ୍ୟ ଦରକାର ତେବେ ପୁନର୍ବାର ଆସନ୍ତୁ। ଆପଣଙ୍କର ଭଲ ଦିନ ହେଉ!",
                                                    "en": "Thank you! Visit again if any help is needed. Have a great day!"
                                                }
                                                await self.voice.speak(farewell.get(self.language, farewell["en"]), self.language)
                                                return True  # Exit flow - application successful
                                            except Exception as e:
                                                logger.error(f"Application error: {e}")
                                        elif confirm_choice is False:
                                            # User said no, ask again which scheme they want
                                            ask_again_msg = {
                                                "en": "I understand. Please tell me which scheme you would like to apply for from the eligible schemes.",
                                                "te": "నేను అర్థం చేసుకున్నాను. దయచేసి మీరు అర్హత కలిగిన స్కీమ్‌ల నుండి ఏ స్కీమ్‌కు దరఖాస్తు చేయాలనుకుంటున్నారో చెప్పండి.",
                                                "ta": "நான் புரிந்துகொண்டேன். தயவுசெய்து தகுதியான திட்டங்களில் எந்த திட்டத்திற்கு விண்ணப்பிக்க விரும்புகிறீர்கள் என்று சொல்லுங்கள்.",
                                                "mr": "मला समजले. कृपया तुम्ही पात्र योजनांपैकी कोणत्या योजनेसाठी अर्ज करू इच्छिता ते सांगा.",
                                                "bn": "আমি বুঝেছি। অনুগ্রহ করে যোগ্য স্কিমগুলির মধ্যে কোন স্কিমের জন্য আবেদন করতে চান তা বলুন।",
                                                "or": "ମୁଁ ବୁଝି ପାରିଲି। ଦୟାକରି ଆପଣ ଯୋଗ୍ୟ ଯୋଜନାଗୁଡ଼ିକ ମଧ୍ୟରୁ କେଉଁଟି ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି ତାହା କହନ୍ତୁ।"
                                            }
                                            await self.voice.speak(ask_again_msg.get(self.language, ask_again_msg["en"]), self.language)
                                            # Continue the loop by asking again (will be handled by the outer flow)
                                    else:
                                        # No valid scheme match found, ask user to clarify
                                        clarify_msg = {
                                            "en": "I couldn't understand which scheme you mentioned. Please tell me the name of the scheme you want to apply for.",
                                            "te": "మీరు చెప్పిన స్కీమ్‌ను నేను అర్థం చేసుకోలేకపోయాను. దయచేసి మీరు దరఖాస్తు చేయాలనుకునే స్కీమ్‌పేరును చెప్పండి.",
                                            "ta": "நீங்கள் குறிப்பிட்ட திட்டத்தை எனக்கு புரியவில்லை. தயவுசெய்து நீங்கள் விண்ணப்பிக்க விரும்பும் திட்டத்தின் பெயரைச் சொல்லுங்கள்.",
                                            "mr": "तुम्ही कोणती योजना म्हणाली हे मला समजले नाही. कृपया तुम्हाला कोणत्या योजनेसाठी अर्ज करायचा आहे ते नाव सांगा.",
                                            "bn": "আপনি কোন স্কিম উল্লেখ করেছেন তা আমি বুঝতে পারিনি। অনুগ্রহ করে আপনি কোন স্কিমের জন্য আবেদন করতে চান তার নাম বলুন।",
                                            "or": "ଆପଣ କେଉଁ ଯୋଜନା ଉଲ୍ଲେଖ କରିଛନ୍ତି ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ଆପଣ କେଉଁଟି ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି ତାହାର ନାମ କହନ୍ତୁ।"
                                        }
                                        await self.voice.speak(clarify_msg.get(self.language, clarify_msg["en"]), self.language)
                                else:
                                    # No voice input received, ask again
                                    no_input_msg = {
                                        "en": "I couldn't hear you clearly. Please tell me which scheme you would like to apply for.",
                                        "te": "నేను మిమ్మల్ని స్పష్టంగా వినలేకపోయాను. దయచేసి మీరు ఏ స్కీమ్‌కు దరఖాస్తు చేయాలనుకుంటున్నారో చెప్పండి.",
                                        "ta": "நான் உங்களை தெளிவாகக் கேட்க முடியவில்லை. தயவுசெய்து நீங்கள் எந்த திட்டத்திற்கு விண்ணப்பிக்க விரும்புகிறீர்கள் என்று சொல்லுங்கள்.",
                                        "mr": "मी तुम्हाला स्पष्ट ऐकू शकलो नाही. कृपया तुम्हाला कोणत्या योजनेसाठी अर्ज करायचा आहे ते सांगा.",
                                        "bn": "আমি আপনাকে স্পষ্টভাবে শুনতে পারিনি। অনুগ্রহ করে কোন স্কিমের জন্য আবেদন করতে চান তা বলুন।",
                                        "or": "ମୁଁ ଆପଣଙ୍କୁ ସ୍ପଷ୍ଟ ଭାବରେ ଶୁଣି ପାରିଲି ନାହିଁ। ଦୟାକରି ଆପଣ କେଉଁଟି ପାଇଁ ଆବେଦନ କରିବାକୁ ଚାହୁଁଛନ୍ତି ତାହା କହନ୍ତୁ।"
                                    }
                                    await self.voice.speak(no_input_msg.get(self.language, no_input_msg["en"]), self.language)
                            
                            # If user says no to applying, show all eligible schemes and handle no eligible schemes case
                            elif apply_general is False:
                                # Show all eligible schemes
                                if matched:
                                    all_eligible_lines = [f"• {s.get('name')} ({s.get('english_name')})" for s in matched]
                                    show_eligible_msg = {
                                        "en": "Here are all the schemes you are eligible for based on your information: \n" + "\n".join(all_eligible_lines),
                                        "te": "మీ సమాచారం ఆధారంగా మీరు అర్హత కలిగిన అన్ని స్కీమ్‌లు ఇవి: \n" + "\n".join(all_eligible_lines),
                                        "ta": "உங்கள் தகவலின் அடிப்படையில் நீங்கள் தகுதியான அனைத்து திட்டங்கள் இவை: \n" + "\n".join(all_eligible_lines),
                                        "mr": "तुमच्या माहितीच्या आधारे तुम्ही पात्र असलेल्या सर्व योजना येथे आहेत: \n" + "\n".join(all_eligible_lines),
                                        "bn": "আপনার তথ্যের ভিত্তিতে আপনি যোগ্য সমস্ত স্কিমগুলি এখানে রয়েছে: \n" + "\n".join(all_eligible_lines),
                                        "or": "ଆପଣଙ୍କର ସୂଚନା ଅନୁସାରେ ଆପଣ ଯୋଗ୍ୟ ସମସ୍ତ ଯୋଜନାଗୁଡ଼ିକ ଏଠାରେ ଅଛନ୍ତି: \n" + "\n".join(all_eligible_lines)
                                    }
                                    await self.voice.speak(show_eligible_msg.get(self.language, show_eligible_msg["en"]), self.language)
                                    return False  # Continue to "enough help?" loop
                                else:
                                    # No eligible schemes - ask if they want to see all available schemes
                                    no_eligible_msg = {
                                        "en": "Based on your information, there are no schemes that you are currently eligible for. Would you like me to display all available schemes? Please say yes or no.",
                                        "te": "మీ సమాచారం ఆధారంగా, మీరు ప్రస్తుతం అర్హత కలిగిన స్కీమ్‌లు లేవు. మీరు అందుబాటులో ఉన్న అన్ని స్కీమ్‌లను ప్రదర్శించాలనుకుంటున్నారా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                        "ta": "உங்கள் தகவலின் அடிப்படையில், நீங்கள் தற்போது தகுதியான திட்டங்கள் எதுவும் இல்லை. கிடைக்கக்கூடிய அனைத்து திட்டங்களையும் காட்ட விரும்புகிறீர்களா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                        "mr": "तुमच्या माहितीच्या आधारे, तुम्ही सध्या पात्र असलेल्या योजना नाहीत. तुम्हाला सर्व उपलब्ध योजना दाखवायच्या आहेत का? कृपया हो किंवा नाही बोला.",
                                        "bn": "আপনার তথ্যের ভিত্তিতে, বর্তমানে আপনার যোগ্য কোনো স্কিম নেই। আপনি সমস্ত উপলব্ধ স্কিম দেখতে চান? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                        "or": "ଆପଣଙ୍କର ସୂଚନା ଅନୁସାରେ, ଆପଣ ବର୍ତ୍ତମାନ ଯୋଗ୍ୟ କୌଣସି ଯୋଜନା ନାହିଁ। ଆପଣ ସମସ୍ତ ଉପଲବ୍ଧ ଯୋଜନାଗୁଡ଼ିକୁ ଦେଖାଇବାକୁ ଚାହୁଁଛନ୍ତି କି? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                                    }
                                    await self.voice.speak(no_eligible_msg.get(self.language, no_eligible_msg["en"]), self.language)
                                    
                                    show_all_decision = None
                                    for show_attempt in range(3):
                                        show_voice = await self.voice.listen(self.language)
                                        try:
                                            show_all_decision = _is_yes(show_voice, self.language)
                                            if show_all_decision is not None:
                                                break
                                        except Exception:
                                            pass
                                        if show_attempt < 2:
                                            repeat_msg = {
                                                "en": "Sorry, I didn't understand. Please say yes or no.",
                                                "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                                "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                                "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                                                "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                                "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                                            }
                                            await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                                    
                                    if show_all_decision is True:
                                        # Show all available schemes
                                        all_schemes = schemes_db.get("schemes", [])
                                        if all_schemes:
                                            all_lines = [f"• {s.get('name')} ({s.get('english_name')})" for s in all_schemes]
                                            all_schemes_text = {
                                                "en": "Here are all available schemes: \n" + "\n".join(all_lines),
                                                "te": "ఇక్కడ అందుబాటులో ఉన్న అన్ని స్కీమ్‌లు ఇవి: \n" + "\n".join(all_lines),
                                                "ta": "கிடைக்கக்கூடிய அனைத்து திட்டங்கள் இங்கே: \n" + "\n".join(all_lines),
                                                "mr": "येथे सर्व उपलब्ध योजना आहेत: \n" + "\n".join(all_lines),
                                                "bn": "এখানে সমস্ত উপলব্ধ স্কিম রয়েছে: \n" + "\n".join(all_lines),
                                                "or": "ଏଠାରେ ସମସ୍ତ ଉପଲବ୍ଧ ଯୋଜନାଗୁଡ଼ିକ ଅଛନ୍ତି: \n" + "\n".join(all_lines)
                                            }
                                            await self.voice.speak(all_schemes_text.get(self.language, all_schemes_text["en"]), self.language)
                                    elif show_all_decision is False:
                                        # User only wants eligible schemes (which are none)
                                        only_eligible_msg = {
                                            "en": "I understand. I will only provide schemes that you are eligible for. Unfortunately, based on your current information, there are no eligible schemes at this time.",
                                            "te": "నేను అర్థం చేసుకున్నాను. నేను మీరు అర్హత కలిగిన స్కీమ్‌లను మాత్రమే అందిస్తాను. దురదృష్టవశాత్తు, మీ ప్రస్తుత సమాచారం ఆధారంగా, ఈ సమయంలో అర్హత కలిగిన స్కీమ్‌లు లేవు.",
                                            "ta": "நான் புரிந்துகொண்டேன். நீங்கள் தகுதியான திட்டங்களை மட்டுமே வழங்குவேன். துரதிர்ஷ்டவசமாக, உங்கள் தற்போதைய தகவலின் அடிப்படையில், இந்த நேரத்தில் தகுதியான திட்டங்கள் எதுவும் இல்லை.",
                                            "mr": "मला समजले. मी फक्त तुम्ही पात्र असलेल्या योजना देईन. दुर्दैवाने, तुमच्या सध्याच्या माहितीच्या आधारे, यावेळी पात्र योजना नाहीत.",
                                            "bn": "আমি বুঝতে পেরেছি। আমি শুধুমাত্র আপনার যোগ্য স্কিমগুলি প্রদান করব। দুর্ভাগ্যবশত, আপনার বর্তমান তথ্যের ভিত্তিতে, এই মুহূর্তে কোন যোগ্য স্কিম নেই।",
                                            "or": "ମୁଁ ବୁଝି ପାରିଲି। ମୁଁ କେବଳ ଆପଣଙ୍କ ଯୋଗ୍ୟ ଯୋଜନାଗୁଡ଼ିକୁ ପ୍ରଦାନ କରିବି। ଦୁର୍ଭାଗ୍ୟବଶତଃ, ଆପଣଙ୍କର ବର୍ତ୍ତମାନର ସୂଚନା ଅନୁସାରେ, ଏହି ସମୟରେ କୌଣସି ଯୋଗ୍ୟ ଯୋଜନା ନାହିଁ।"
                                        }
                                        await self.voice.speak(only_eligible_msg.get(self.language, only_eligible_msg["en"]), self.language)
                                    
                                    return False  # Continue to "enough help?" loop
                else:
                    no_match_text = {
                        "en": "I could not confidently match schemes yet. I will ask a few more questions.",
                        "te": "ఇంకా సరైన స్కీమ్‌లను ఖచ్చితంగా కలపలేకపోయాను. మరికొన్ని ప్రశ్నలు అడుగుతాను.",
                        "ta": "இன்னும் திட்டங்களை உறுதியாக பொருத்த முடியவில்லை. சில கேள்விகள் கேட்கிறேன்.",
                        "mr": "अजून योजना जुळवता आल्या नाहीत. काही प्रश्न विचारतो.",
                        "bn": "এখনো নিশ্চিতভাবে স্কিম মিলাতে পারিনি। আরও কয়েকটি প্রশ্ন করব।",
                        "or": "ଏପର୍ଯ୍ୟନ୍ତ ଯୋଜନା ସ୍ପଷ୍ଟ ହେଲା ନାହିଁ। କିଛି ପ୍ରଶ୍ନ ପଚରିବି।"
                    }
                    await self.voice.speak(no_match_text.get(self.language, no_match_text["en"]), self.language)
            except Exception as e:
                logger.error(f"Eligibility computation error: {e}")
            
            return False  # Indicate no application was made
        
        # Initial profile gathering and scheme display (language is already set, won't be asked again)
        application_successful = await gather_profile_and_show_schemes()
        
        # If application was successful, end the session
        if application_successful:
            return
        
        # Loop for re-asking profile details when user says "no" (language stays the same)
        while True:
            # Ask if this is enough and allow voice exit (double prompt)
            enough_msg_1 = {
                "en": "Is this enough help for now? Please say yes or no.",
                "te": "ఇది సరిపోతుందా? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                "ta": "இதனால் போதுமா? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                "mr": "हे पुरेसे आहे का? कृपया हो किंवा नाही बोला.",
                "bn": "এগুলো কি যথেষ্ট? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                "or": "ଏହା ପର୍ଯ୍ୟାପ୍ତ କି? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
            }
            # Get first confirmation with voice-only retry
            enough_decision_1 = None
            for attempt_1 in range(3):
                await self.voice.speak(enough_msg_1.get(self.language, enough_msg_1["en"]), self.language)
                enough_voice_1 = await self.voice.listen(self.language)
                try:
                    enough_decision_1 = _is_yes(enough_voice_1, self.language)
                    if enough_decision_1 is not None:
                        break
                except Exception:
                    pass
                if attempt_1 < 2:
                    repeat_msg = {
                        "en": "Sorry, I didn't understand. Please say yes or no.",
                        "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                        "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                        "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                        "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                        "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                    }
                    await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
            
            # Double prompt - ask again to confirm if first was yes
            if enough_decision_1 is True:
                confirm_msg = {
                    "en": "Are you sure you have enough help? Please confirm yes or no.",
                    "te": "మీకు తగినంత సహాయం లభించిందని మీరు ఖచ్చితంగా అనుకుంటున్నారా? దయచేసి అవును లేదా కాదు అని నిర్ధారించండి.",
                    "ta": "தங்களுக்கு போதுமான உதவி கிடைத்தது என்பது உறுதியா? தயவுசெய்து ஆம் அல்லது இல்லை என உறுதிப்படுத்துங்கள்.",
                    "mr": "तुम्हाला पुरेसे मदत मिळाली आहे याची खात्री आहे का? कृपया हो किंवा नाही निश्चित करा.",
                    "bn": "আপনি কি নিশ্চিত যে আপনার যথেষ্ট সাহায্য হয়েছে? অনুগ্রহ করে হ্যাঁ বা না নিশ্চিত করুন।",
                    "or": "ଆପଣଙ୍କର ଯଥେଷ୍ଟ ସାହାଯ୍ୟ ମିଳିଛି ବୋଲି ଆପଣ ନିଶ୍ଚିତ କି? ଦୟାକରି ହଁ କିମ୍ବା ନା ନିଶ୍ଚିତ କରନ୍ତୁ।"
                }
                enough_decision_2 = None
                for attempt_2 in range(3):
                    await self.voice.speak(confirm_msg.get(self.language, confirm_msg["en"]), self.language)
                    enough_voice_2 = await self.voice.listen(self.language)
                    try:
                        enough_decision_2 = _is_yes(enough_voice_2, self.language)
                        if enough_decision_2 is not None:
                            break
                    except Exception:
                        pass
                    if attempt_2 < 2:
                        repeat_msg = {
                            "en": "Sorry, I didn't understand. Please say yes or no.",
                            "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                            "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                            "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                            "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                            "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                        }
                        await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                
                if enough_decision_2 is True:
                    # User confirmed "yes" twice - end session with farewell message
                    farewell = {
                        "te": "ధన్యవాదాలు! ఏదైనా సహాయం అవసరమైతే మళ్లీ సందర్శించండి. మీకు మంచి రోజు కలగాలి!",
                        "ta": "நன்றி! எந்த உதவி தேவைப்பட்டால் மீண்டும் வாருங்கள். உங்களுக்கு நல்ல நாள் வேண்டும்!",
                        "mr": "धन्यवाद! जर काही मदत हवी असेल तर पुन्हा भेट द्या. तुमचा दिवस चांगला जावो!",
                        "bn": "ধন্যবাদ! আর কোন সাহায্যের প্রয়োজন হলে আবার আসুন। আপনার ভাল দিন হোক!",
                        "or": "ଧନ୍ୟବାଦ! ଯଦି ଆହୁରି ସାହାଯ୍ୟ ଦରକାର ତେବେ ପୁନର୍ବାର ଆସନ୍ତୁ। ଆପଣଙ୍କର ଭଲ ଦିନ ହେଉ!",
                        "en": "Thank you! Visit again if any help is needed. Have a great day!"
                    }
                    await self.voice.speak(farewell.get(self.language, farewell["en"]), self.language)
                    print("Session ended as user confirmed they have enough help.")
                    return
            
            # User said "no" - re-ask profile questions and show schemes again
            if enough_decision_1 is False or (enough_decision_1 is True and enough_decision_2 is False):
                # User said "no" - re-ask profile questions and show schemes again
                reask_msg = {
                    "en": "Let me ask you your details again to find the right programs for you.",
                    "te": "మీకు సరైన ప్రోగ్రామ్‌లను కనుగొనడానికి మళ్లీ మీ వివరాలను అడుగుతున్నాను.",
                    "ta": "உங்களுக்கு சரியான திட்டங்களைக் கண்டுபிடிக்க உங்கள் விவரங்களை மீண்டும் கேட்கிறேன்.",
                    "mr": "तुम्हाला योग्य कार्यक्रम सापडावेत म्हणून मी तुमच्या तपशीलांना पुन्हा विचारत आहे.",
                    "bn": "আপনার জন্য সঠিক প্রোগ্রাম খুঁজে পেতে আমি আবার আপনার বিবরণ জিজ্ঞাসা করছি।",
                    "or": "ଆପଣଙ୍କ ପାଇଁ ଠିକ୍ ପ୍ରୋଗ୍ରାମ୍ ଖୋଜିବା ପାଇଁ ମୁଁ ଆପଣଙ୍କର ବିବରଣୀ ପୁନର୍ବାର ପଚାରୁଛି।"
                }
                await self.voice.speak(reask_msg.get(self.language, reask_msg["en"]), self.language)
                # Re-gather profile and show schemes
                application_successful = await gather_profile_and_show_schemes()
                # If application was successful, end the session
                if application_successful:
                    return
                # Continue the loop to ask "enough help?" again
                continue
        
        # Continue to conversation loop after user confirmed they have enough help
        while True:
            try:
                print("\n" + "="*60)
                
                # Listen to user
                user_input = await self.voice.listen(self.language)
                
                # Check for quit commands
                if user_input and any(word in user_input.lower() for word in ["quit", "exit", "bye", "goodbye"]):
                    farewell = {
                        "te": "ధన్యవాదాలు! మీకు మంచి రోజు కలగాలి!",
                        "ta": "நன்றி! உங்களுக்கு நல்ல நாள் வேண்டும்!",
                        "mr": "धन्यवाद! तुमचा दिवस चांगला जावो!",
                        "bn": "ধন্যবাদ! আপনার ভাল দিন হোক!",
                        "or": "ଧନ୍ୟବାଦ! ଆପଣଙ୍କର ଭଲ ଦିନ ହେଉ!",
                        "en": "Thank you! Have a great day!"
                    }
                    await self.voice.speak(farewell.get(self.language, farewell["en"]), self.language)
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Check if user is asking about a scheme - if so, ask if they want details first
                # Get all scheme names to check against
                schemes_db_result = await self.tools["scheme_database"].execute({"language": self.language})
                all_schemes = schemes_db_result.get("schemes", [])
                user_input_lower = user_input.lower()
                
                # Check if user input mentions any scheme name
                mentioned_scheme = None
                for scheme in all_schemes:
                    scheme_name = (scheme.get("name") or "").lower()
                    scheme_english = (scheme.get("english_name") or "").lower()
                    if scheme_name and scheme_name in user_input_lower:
                        mentioned_scheme = scheme
                        break
                    if scheme_english and scheme_english in user_input_lower:
                        mentioned_scheme = scheme
                        break
                
                # If user asked about a scheme, ask if they want details first
                if mentioned_scheme:
                    ask_details_msg = {
                        "en": f"Should I display the information needed that helps you for the {mentioned_scheme.get('english_name')} scheme, such as required documents, where to apply, and the application process? Please say yes or no.",
                        "te": f"నేను {mentioned_scheme.get('name')} స్కీమ్‌కు మీకు సహాయపడే సమాచారాన్ని ప్రదర్శించాలా? ఉదాహరణకు, అవసరమైన పత్రాలు, ఎక్కడ దరఖాస్తు చేయాలి, మరియు దరఖాస్తు ప్రక్రియ? దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                        "ta": f"நான் {mentioned_scheme.get('name')} திட்டத்திற்கு உங்களுக்கு உதவும் தகவல்களை காட்ட வேண்டுமா? எடுத்துக்காட்டாக, தேவையான ஆவணங்கள், எங்கு விண்ணப்பிக்க வேண்டும், மற்றும் விண்ணப்ப செயல்முறை? தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                        "mr": f"मी {mentioned_scheme.get('name')} योजनेसाठी तुम्हाला मदत करणारी माहिती दाखवावी का? उदाहरणार्थ, आवश्यक कागदपत्रे, कोठे अर्ज करायचा, आणि अर्ज प्रक्रिया? कृपया हो किंवा नाही बोला.",
                        "bn": f"আমি কি {mentioned_scheme.get('name')} স্কিমের জন্য আপনার প্রয়োজনীয় তথ্য প্রদর্শন করব? উদাহরণস্বরূপ, প্রয়োজনীয় নথি, কোথায় আবেদন করবেন, এবং আবেদনের প্রক্রিয়া? অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                        "or": f"ମୁଁ {mentioned_scheme.get('name')} ଯୋଜନା ପାଇଁ ଆପଣଙ୍କୁ ସାହାଯ୍ୟ କରୁଥିବା ସୂଚନା ପ୍ରଦର୍ଶନ କରିବି କି? ଉଦାହରଣ ସ୍ୱରୂପ, ଆବଶ୍ୟକ ଦସ୍ତାବେଜ, କେଉଁଠାରେ ଆବେଦନ କରିବେ, ଏବଂ ଆବେଦନ ପ୍ରକ୍ରିୟା? ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                    }
                    await self.voice.speak(ask_details_msg.get(self.language, ask_details_msg["en"]), self.language)
                    
                    want_details = None
                    for detail_attempt in range(3):
                        detail_voice = await self.voice.listen(self.language)
                        try:
                            want_details = _is_yes(detail_voice, self.language)
                            if want_details is not None:
                                break
                        except Exception:
                            pass
                        if detail_attempt < 2:
                            repeat_msg = {
                                "en": "Sorry, I didn't understand. Please say yes or no.",
                                "te": "క్షమించండి, నేను అర్థం చేసుకోలేదు. దయచేసి అవును లేదా కాదు అని చెప్పండి.",
                                "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
                                "mr": "माफ करा, मला समजले नाही. कृपया हो किंवा नाही बोला.",
                                "bn": "দুঃখিত, আমি বুঝতে পারিনি। অনুগ্রহ করে হ্যাঁ বা না বলুন।",
                                "or": "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ହଁ କିମ୍ବା ନା କହନ୍ତୁ।"
                            }
                            await self.voice.speak(repeat_msg.get(self.language, repeat_msg["en"]), self.language)
                    
                    # If user wants details, show them before processing
                    if want_details is True:
                        doc_list = mentioned_scheme.get("documents", [])
                        where = mentioned_scheme.get("where_to_apply")
                        steps = mentioned_scheme.get("apply_steps", [])
                        guidance_lines = []
                        if doc_list:
                            guidance_lines.append(({
                                "en": "Required documents:",
                                "te": "అవసరమైన పత్రాలు:",
                                "ta": "தேவையான ஆவணங்கள்:",
                                "mr": "आवश्यक कागदपत्रे:",
                                "bn": "প্রয়োজনীয় নথি:",
                                "or": "ଆବଶ୍ୟକ ଦସ୍ତାବେଜ:",
                            }).get(self.language, "Required documents:") + " " + ", ".join(doc_list))
                        if where:
                            guidance_lines.append(({
                                "en": "Where to apply:",
                                "te": "ఎక్కడ దరఖాస్తు చేయాలి:",
                                "ta": "எங்கு விண்ணப்பிக்க வேண்டும்:",
                                "mr": "कोठे अर्ज करायचा:",
                                "bn": "কোথায় আবেদন করবেন:",
                                "or": "କେଉଁଠାରେ ଆବେଦନ କରିବେ:",
                            }).get(self.language, "Where to apply:") + f" {where}")
                        if steps:
                            numbered = [f"{i+1}. {st}" for i, st in enumerate(steps)]
                            guidance_lines.append(({
                                "en": "Steps to apply:",
                                "te": "అప్లై చేసే దశలు:",
                                "ta": "விண்ணப்பிக்கும் படிகள்:",
                                "mr": "अर्ज करण्याच्या पायऱ्या:",
                                "bn": "আবেদনের ধাপসমূহ:",
                                "or": "ଆବେଦନ ପଦକ୍ରମ:",
                            }).get(self.language, "Steps to apply:") + " \n" + "\n".join(numbered))
                        
                        if guidance_lines:
                            scheme_details_msg = {
                                "en": f"For {mentioned_scheme.get('english_name')}: \n" + "\n".join(guidance_lines),
                                "te": f"{mentioned_scheme.get('name')} కోసం: \n" + "\n".join(guidance_lines),
                                "ta": f"{mentioned_scheme.get('name')} க்காக: \n" + "\n".join(guidance_lines),
                                "mr": f"{mentioned_scheme.get('name')} साठी: \n" + "\n".join(guidance_lines),
                                "bn": f"{mentioned_scheme.get('name')} এর জন্য: \n" + "\n".join(guidance_lines),
                                "or": f"{mentioned_scheme.get('name')} ପାଇଁ: \n" + "\n".join(guidance_lines),
                            }
                            await self.voice.speak(scheme_details_msg.get(self.language, scheme_details_msg["en"]), self.language)
                
                # Process and respond (whether details were shown or not)
                response = await self.process_user_input(user_input)
                
                # Small pause for natural conversation flow
                await asyncio.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted.")
                break
            except Exception as e:
                logger.error(f"Voice session error: {e}")
                error_msg = "I'm sorry, I encountered an error. Please try again."
                print(f"Error: {e}")
                await self.voice.speak(error_msg, "en")
                
        print("\n=== Voice Session Ended ===")

    async def run_demo(self):
        """Run demo with predefined interactions"""
        logger.info("Running demo scenario...")
        
        demo_inputs = {
            "te": [
                "నాకు సरकार స్కీమ్ కోసం దరఖాస్తు చేయవాలి",
                "నా వయస్సు 65 సంవత్సరాలు",
                "నా సంవత్సర ఆదాయం 40000 రూపాయలు"
            ],
            "ta": [
                "எனக்கு அரசு திட்டத்திற்கு விண்ணப்பிக்க வேண்டும்",
                "என் வயது 28 ஆண்டுகள்",
                "எனக்கு கல்வி ஆதரவு தேவை"
            ],
            "mr": [
                "मुझे सरकारी योजना के लिए आवेदन करना है",
                "मेरी उम्र 55 साल है",
                "मेरी आय 30000 रुपये प्रति वर्ष है"
            ]
        }
        
        inputs = demo_inputs.get(self.language, demo_inputs["te"])
        
        for user_input in inputs:
            print(f"\nUser: {user_input}")
            response = await self.process_user_input(user_input)
            print(f"Agent: {response}")
            await asyncio.sleep(1)
        
        print("\n=== Demo Complete ===")
        print(f"Memory Stats: {self.memory.get_statistics()}")

    async def evaluate_agent(self):
        """Evaluate agent with different scenarios"""
        logger.info("Running agent evaluation...")
        
        test_scenarios = [
            {
                "name": "Basic Eligibility Query",
                "input": "I want to know which schemes I'm eligible for",
                "language": "te"
            },
            {
                "name": "Incomplete Information",
                "input": "Apply for pension but I'm only 45 years old",
                "language": "te"
            },
            {
                "name": "Document Upload",
                "input": "I've uploaded all documents for my application",
                "language": "ta"
            },
            {
                "name": "Contradiction Handling",
                "input": "My income is 50000... wait, it's actually 30000",
                "language": "mr"
            }
        ]
        
        results = []
        for scenario in test_scenarios:
            logger.info(f"Testing: {scenario['name']}")
            self.language = scenario['language']
            self.agent.llm = create_llm_provider("mock")
            
            response = await self.process_user_input(scenario['input'])
            
            results.append({
                "scenario": scenario['name'],
                "status": "success" if response else "failed",
                "response_length": len(response)
            })
        
        return results


async def main():
    """Main entry point"""
    load_dotenv()
    
    import sys
    
    # Parse command line arguments
    mode = "voice"  # default - voice-first is mandatory
    language = "te"  # default to Telugu (native language support)
    voice_mode = "local"  # default to local voice (voice input/output mandatory)
    llm_provider = "mock"  # default
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["demo", "evaluate", "interactive", "voice"]:
            mode = sys.argv[1]
        if len(sys.argv) > 2:
            language = sys.argv[2]
        if len(sys.argv) > 3:
            voice_mode = sys.argv[3]
    
    # Create agent
    agent = WelfareAgent(
        language=language,
        llm_provider=llm_provider,
        voice_mode=voice_mode,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Choose mode
    if mode == "demo":
        await agent.run_demo()
    elif mode == "evaluate":
        results = await agent.evaluate_agent()
        print("\n=== Evaluation Results ===")
        for result in results:
            print(f"{result['scenario']}: {result['status']} ({result['response_length']} chars)")
    elif mode == "voice":
        await agent.voice_session()
    elif mode == "interactive":
        # Text-based mode (for testing only)
        await agent.interactive_session()
    else:
        # Default: Voice-first mode (mandatory requirement)
        await agent.voice_session()


if __name__ == "__main__":
    asyncio.run(main())
