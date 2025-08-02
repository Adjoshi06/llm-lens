"""
Python SDK for monitoring LLM API calls.
"""
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import functools
import logging

logger = logging.getLogger(__name__)


class LLMMonitor:
    """Monitor for tracking LLM API calls."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize LLM Monitor.
        
        Args:
            api_url: URL of the LLM Monitor API
        """
        self.api_url = api_url.rstrip("/")
        self.events_endpoint = f"{self.api_url}/api/events"
    
    def track(
        self,
        tags: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ):
        """
        Decorator to track LLM API calls.
        
        Args:
            tags: Optional dictionary of tags to attach to the event
            model: Optional model name (if not provided, will try to extract from response)
            
        Usage:
            @monitor.track(tags={"user_id": "123"})
            def my_llm_call():
                response = openai.chat.completions.create(...)
                return response
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                error_message = None
                response = None
                
                try:
                    # Call the original function
                    response = func(*args, **kwargs)
                    
                    # Extract model and token information from response
                    model_name = model
                    prompt_tokens = None
                    completion_tokens = None
                    total_tokens = None
                    
                    # Try to extract from OpenAI response
                    if hasattr(response, 'model'):
                        model_name = model_name or response.model
                    if hasattr(response, 'usage'):
                        usage = response.usage
                        if hasattr(usage, 'prompt_tokens'):
                            prompt_tokens = usage.prompt_tokens
                        if hasattr(usage, 'completion_tokens'):
                            completion_tokens = usage.completion_tokens
                        if hasattr(usage, 'total_tokens'):
                            total_tokens = usage.total_tokens
                    
                    # Calculate latency
                    latency_ms = int((time.time() - start_time) * 1000)
                    
                    # Log event
                    self._log_event(
                        model=model_name or "unknown",
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        latency_ms=latency_ms,
                        status=status,
                        tags=tags
                    )
                    
                    return response
                    
                except Exception as e:
                    status = "error"
                    error_message = str(e)
                    latency_ms = int((time.time() - start_time) * 1000)
                    
                    # Log error event
                    self._log_event(
                        model=model or "unknown",
                        prompt_tokens=None,
                        completion_tokens=None,
                        total_tokens=None,
                        latency_ms=latency_ms,
                        status=status,
                        error_message=error_message,
                        tags=tags
                    )
                    
                    # Re-raise the exception
                    raise
            
            return wrapper
        return decorator
    
    def log_event(
        self,
        model: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        latency_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Manually log an LLM event.
        
        Args:
            model: Model name
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            total_tokens: Total number of tokens
            latency_ms: Latency in milliseconds
            status: Status ("success" or "error")
            error_message: Error message if status is "error"
            tags: Optional dictionary of tags
            timestamp: Optional timestamp (defaults to now)
        """
        self._log_event(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            tags=tags,
            timestamp=timestamp or datetime.utcnow()
        )
    
    def _log_event(
        self,
        model: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        latency_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Internal method to log an event to the API.
        
        Args:
            model: Model name
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            total_tokens: Total number of tokens
            latency_ms: Latency in milliseconds
            status: Status ("success" or "error")
            error_message: Error message if status is "error"
            tags: Optional dictionary of tags
            timestamp: Optional timestamp (defaults to now)
        """
        try:
            event_data = {
                "timestamp": (timestamp or datetime.utcnow()).isoformat() + "Z",
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
                "status": status,
                "error_message": error_message,
                "tags": tags
            }
            
            response = requests.post(
                self.events_endpoint,
                json=event_data,
                timeout=5
            )
            response.raise_for_status()
            
        except Exception as e:
            # Log error but don't raise - we don't want to break the application
            logger.warning(f"Failed to log event to LLM Monitor: {e}")

