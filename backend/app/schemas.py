"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID


class LLMEventCreate(BaseModel):
    """Schema for creating a new LLM event."""
    timestamp: datetime
    model: str = Field(..., max_length=100)
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    status: str = Field(..., pattern="^(success|error)$")
    error_message: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-01T00:00:00Z",
                "model": "gpt-4",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 850,
                "cost_usd": 0.003,
                "status": "success",
                "tags": {"user_id": "123", "feature": "chat"}
            }
        }


class LLMEventResponse(BaseModel):
    """Schema for LLM event response."""
    id: UUID
    timestamp: datetime
    model: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    latency_ms: Optional[int]
    cost_usd: Optional[float]
    status: str
    error_message: Optional[str]
    tags: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsOverviewResponse(BaseModel):
    """Schema for metrics overview response."""
    total_requests: int
    total_cost: float
    avg_latency_ms: float
    error_rate: float
    requests_by_model: Dict[str, int]


class TimeSeriesDataPoint(BaseModel):
    """Schema for a single time-series data point."""
    timestamp: datetime
    value: float
    model: Optional[str] = None


class TimeSeriesResponse(BaseModel):
    """Schema for time-series response."""
    data: List[TimeSeriesDataPoint]


class ConversationsResponse(BaseModel):
    """Schema for conversations/events list response."""
    events: List[LLMEventResponse]
    total: int
    page: int
    page_size: int

