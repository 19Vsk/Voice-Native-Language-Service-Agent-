#!/usr/bin/env python3
"""
Test runner for welfare agent system
Run: python test_runner.py
"""
import asyncio
import sys
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)


async def test_voice_interface():
    """Test voice interface"""
    print("\n[TEST] Voice Interface")
    print("-" * 50)
    
    try:
        from src.voice.interface import create_voice_interface
        
        # Test mock interface
        voice = create_voice_interface("mock")
        
        # Test listen
        text = await voice.listen("te")
        assert text, "STT should return text"
        print(f"  ✓ STT: Captured '{text[:30]}...'")
        
        # Test speak
        await voice.speak("నమస్కారం", "te")
        print(f"  ✓ TTS: Generated speech for Telugu")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_agent_state_machine():
    """Test agent state machine"""
    print("\n[TEST] Agent State Machine")
    print("-" * 50)
    
    try:
        from src.agent.core import Agent, AgentState
        from src.agent.llm_provider import create_llm_provider
        from src.voice.interface import create_voice_interface
        from src.memory.manager import ConversationMemory
        from src.tools.implementations import SchemeDatabase, EligibilityChecker
        
        llm = create_llm_provider("mock")
        voice = create_voice_interface("mock")
        memory = ConversationMemory()
        tools = {
            "scheme_database": SchemeDatabase(),
            "eligibility_checker": EligibilityChecker()
        }
        
        agent = Agent(llm, memory, voice, tools)
        
        # Test initial state
        assert agent.state == AgentState.IDLE, "Initial state should be IDLE"
        print("  ✓ Initial state: IDLE")
        
        # Test state transitions
        agent.set_state(AgentState.LISTENING)
        assert agent.state == AgentState.LISTENING, "State should transition"
        print("  ✓ State transition: IDLE → LISTENING")
        
        agent.set_state(AgentState.PROCESSING)
        assert agent.state == AgentState.PROCESSING
        print("  ✓ State transition: LISTENING → PROCESSING")
        
        agent.set_state(AgentState.PLANNING)
        assert agent.state == AgentState.PLANNING
        print("  ✓ State transition: PROCESSING → PLANNING")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_memory_management():
    """Test memory management"""
    print("\n[TEST] Memory Management")
    print("-" * 50)
    
    try:
        from src.memory.manager import ConversationMemory
        
        memory = ConversationMemory()
        
        # Test adding turns
        memory.add_turn("user", "నాకు సాయ్యం కోసం", "te")
        memory.add_turn("assistant", "సరిగ్గా", "te")
        
        assert len(memory.conversation_history) == 2, "Should have 2 turns"
        print(f"  ✓ Conversation history: {len(memory.conversation_history)} turns")
        
        # Test profile update
        memory.update_user_profile({"age": 65})
        assert memory.user_profile["age"] == 65, "Profile should update"
        print(f"  ✓ Profile update: age = 65")
        
        # Test contradiction detection
        memory.update_user_profile({"age": 60})
        assert len(memory.contradiction_log) > 0, "Should detect contradiction"
        print(f"  ✓ Contradiction detected: 65 → 60")
        
        # Test context retrieval
        context = memory.get_context()
        assert "recent_conversation" in context, "Context should have conversation"
        print(f"  ✓ Context retrieval: {len(context)} keys")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_tools():
    """Test tool implementations"""
    print("\n[TEST] Tool Implementations")
    print("-" * 50)
    
    try:
        from src.tools.implementations import (
            SchemeDatabase, EligibilityChecker,
            ApplicationTracker, UserProfileBuilder
        )
        
        # Test SchemeDatabase
        db = SchemeDatabase()
        result = await db.execute({"language": "te"})
        assert result["schemes"], "Should return schemes"
        print(f"  ✓ SchemeDatabase: {result['total_count']} schemes found")
        
        # Test EligibilityChecker
        checker = EligibilityChecker()
        result = await checker.execute({
            "user_profile": {
                "age": 65,
                "annual_income": 40000,
                "category": "General"
            }
        })
        assert "eligible_schemes" in result, "Should return eligibility"
        print(f"  ✓ EligibilityChecker: {len(result['eligible_schemes'])} eligible schemes")
        
        # Test ApplicationTracker
        tracker = ApplicationTracker()
        result = await tracker.execute({
            "action": "create",
            "user_id": "test_user",
            "scheme_name": "Old-Age Pension"
        })
        assert "application_id" in result, "Should create application"
        print(f"  ✓ ApplicationTracker: Application created")
        
        # Test UserProfileBuilder
        builder = UserProfileBuilder()
        result = await builder.execute({
            "user_message": "నాకు 65 సంవత్సరాలు",
            "current_profile": {},
            "language": "te"
        })
        assert "extracted_info" in result, "Should extract info"
        print(f"  ✓ UserProfileBuilder: Info extracted")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_llm_provider():
    """Test LLM providers"""
    print("\n[TEST] LLM Providers")
    print("-" * 50)
    
    try:
        from src.agent.llm_provider import create_llm_provider
        
        # Test mock provider
        llm = create_llm_provider("mock")
        response = await llm.call("Test prompt", "te")
        assert response, "Should return response"
        print(f"  ✓ Mock LLM: Response generated")
        
        # Test provider factory
        mock_llm = create_llm_provider("mock")
        assert mock_llm is not None, "Should create mock provider"
        print(f"  ✓ Provider factory: Mock provider created")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_agent_workflow():
    """Test full agent workflow"""
    print("\n[TEST] Agent Workflow")
    print("-" * 50)
    
    try:
        from src.agent.core import Agent
        from src.agent.llm_provider import create_llm_provider
        from src.voice.interface import create_voice_interface
        from src.memory.manager import ConversationMemory
        from src.tools.implementations import (
            SchemeDatabase, EligibilityChecker,
            ApplicationTracker, UserProfileBuilder
        )
        
        llm = create_llm_provider("mock")
        voice = create_voice_interface("mock")
        memory = ConversationMemory()
        tools = {
            "scheme_database": SchemeDatabase(),
            "eligibility_checker": EligibilityChecker(),
            "application_tracker": ApplicationTracker(),
            "user_profile_builder": UserProfileBuilder()
        }
        
        agent = Agent(llm, memory, voice, tools)
        
        # Run agent
        user_input = "నాకు పెన్షన్ కోసం దరఖాస్తు చేయాలి"
        response = await agent.run(user_input, "te")
        
        assert response, "Should return response"
        print(f"  ✓ Agent workflow: Complete")
        print(f"  ✓ Response: '{response[:50]}...'")
        
        # Check memory
        assert len(memory.conversation_history) > 0, "Should have history"
        print(f"  ✓ Memory: {len(memory.conversation_history)} turns recorded")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_language_support():
    """Test multi-language support"""
    print("\n[TEST] Language Support")
    print("-" * 50)
    
    try:
        from src.agent.core import Agent
        from src.agent.llm_provider import create_llm_provider
        from src.voice.interface import create_voice_interface
        from src.memory.manager import ConversationMemory
        from src.tools.implementations import SchemeDatabase
        
        languages = ["te", "ta", "mr", "bn", "or"]
        
        db = SchemeDatabase()
        
        for lang in languages:
            result = await db.execute({"language": lang})
            assert result["schemes"], f"Should have schemes for {lang}"
            print(f"  ✓ Language {lang.upper()}: {len(result['schemes'])} schemes")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_error_handling():
    """Test error handling"""
    print("\n[TEST] Error Handling")
    print("-" * 50)
    
    try:
        from src.memory.manager import ConversationMemory
        
        memory = ConversationMemory()
        
        # Test graceful degradation on profile update with contradiction
        try:
            memory.update_user_profile({"age": 30})
            memory.update_user_profile({"age": 35})
            print(f"  ✓ Contradiction handling: Handled gracefully")
        except:
            print(f"  ✗ Contradiction handling: Failed")
            return False
        
        # Test memory limits
        for i in range(50):
            memory.add_turn("user", f"Message {i}", "te")
        
        # Should have limited history
        assert len(memory.conversation_history) <= memory.max_history
        print(f"  ✓ Memory limits: Enforced (max {memory.max_history} turns)")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def run_all_tests() -> Dict[str, bool]:
    """Run all tests"""
    tests = [
        ("Voice Interface", test_voice_interface),
        ("Agent State Machine", test_agent_state_machine),
        ("Memory Management", test_memory_management),
        ("Tools", test_tools),
        ("LLM Provider", test_llm_provider),
        ("Agent Workflow", test_agent_workflow),
        ("Language Support", test_language_support),
        ("Error Handling", test_error_handling),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results[test_name] = False
    
    return results


async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("WELFARE AGENT - TEST SUITE".center(80))
    print("="*80)
    
    # Run all tests
    results = await run_all_tests()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*50)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
