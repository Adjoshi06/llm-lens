"""
Pricing tables for different LLM models.
"""
from typing import Optional

# Pricing per 1M tokens (in USD)
PRICING_TABLE = {
    # OpenAI models
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-4-32k": {"input": 60.0, "output": 120.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
    "gpt-4-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-3.5-turbo-16k": {"input": 3.0, "output": 4.0},
    
    # Anthropic models
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0},  # Alias
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.0},
}

# Default pricing for unknown models
DEFAULT_PRICING = {"input": 1.0, "output": 2.0}


def get_pricing(model: str) -> dict:
    """
    Get pricing for a specific model.
    
    Args:
        model: Model name (e.g., "gpt-4", "claude-sonnet-4")
        
    Returns:
        Dictionary with "input" and "output" pricing per 1M tokens
    """
    # Try exact match first
    if model in PRICING_TABLE:
        return PRICING_TABLE[model]
    
    # Try partial match (e.g., "gpt-4-0613" -> "gpt-4")
    for known_model, pricing in PRICING_TABLE.items():
        if model.startswith(known_model):
            return pricing
    
    # Return default pricing
    return DEFAULT_PRICING


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
) -> float:
    """
    Calculate cost in USD based on tokens and model pricing.
    
    Args:
        model: Model name
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        
    Returns:
        Cost in USD
    """
    pricing = get_pricing(model)
    
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    
    total_cost = input_cost + output_cost
    
    return round(total_cost, 6)

