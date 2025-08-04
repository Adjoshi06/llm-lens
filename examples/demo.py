"""
Demo script showing how to use the LLM Monitor SDK.

This script demonstrates how to track LLM API calls using the monitor SDK.

Usage:
    cd examples
    PYTHONPATH=.. python demo.py
"""
import os
import sys
import time
from datetime import datetime

# Add parent directory to path so we can import the app module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.monitor.sdk import LLMMonitor

# Initialize monitor
monitor = LLMMonitor(api_url="http://localhost:8000")


@monitor.track(tags={"user_id": "123", "feature": "chat"})
def chat_completion_simulation(message: str, model: str = "gpt-4"):
    """
    Simulate an LLM API call.
    
    In a real scenario, this would call the actual OpenAI or Anthropic API.
    """
    # Simulate API latency
    time.sleep(0.1)  # 100ms
    
    # Simulate response
    class MockUsage:
        def __init__(self):
            self.prompt_tokens = 50
            self.completion_tokens = 25
            self.total_tokens = 75
    
    class MockResponse:
        def __init__(self, model_name):
            self.model = model_name
            self.usage = MockUsage()
    
    return MockResponse(model)


@monitor.track(tags={"user_id": "456", "feature": "analysis"})
def analysis_completion_simulation(text: str, model: str = "claude-sonnet-4"):
    """
    Simulate another LLM API call with different model.
    """
    time.sleep(0.15)  # 150ms
    
    class MockUsage:
        def __init__(self):
            self.prompt_tokens = 200
            self.completion_tokens = 100
            self.total_tokens = 300
    
    class MockResponse:
        def __init__(self, model_name):
            self.model = model_name
            self.usage = MockUsage()
    
    return MockResponse(model)


def simulate_error():
    """
    Simulate an error scenario.
    """
    try:
        raise ValueError("API rate limit exceeded")
    except Exception as e:
        # Log error event
        monitor.log_event(
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=0,
            total_tokens=100,
            latency_ms=50,
            status="error",
            error_message=str(e),
            tags={"user_id": "789", "feature": "chat"}
        )
        raise


def main():
    """Run demo script."""
    print("LLM Monitor Demo")
    print("=" * 50)
    
    # Simulate successful calls
    print("\n1. Simulating successful GPT-4 call...")
    response = chat_completion_simulation("What is the capital of France?", "gpt-4")
    print(f"   Model: {response.model}, Tokens: {response.usage.total_tokens}")
    
    print("\n2. Simulating successful Claude call...")
    response = analysis_completion_simulation("Analyze this text...", "claude-sonnet-4")
    print(f"   Model: {response.model}, Tokens: {response.usage.total_tokens}")
    
    print("\n3. Simulating error scenario...")
    try:
        simulate_error()
    except ValueError as e:
        print(f"   Error caught: {e}")
    
    # Manual event logging
    print("\n4. Logging manual event...")
    monitor.log_event(
        model="gpt-4-mini",
        prompt_tokens=30,
        completion_tokens=15,
        total_tokens=45,
        latency_ms=200,
        status="success",
        tags={"user_id": "999", "feature": "manual"}
    )
    print("   Manual event logged")
    
    print("\n" + "=" * 50)
    print("Demo complete! Check the dashboard at http://localhost:3000")


if __name__ == "__main__":
    main()

