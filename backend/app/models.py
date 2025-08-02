"""
SQLAlchemy models for LLM monitoring.
"""
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class LLMEvent(Base):
    """Model for storing LLM API call events."""
    __tablename__ = "llm_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(10, 6), nullable=True)
    status = Column(String(20), nullable=False, index=True)  # 'success' or 'error'
    error_message = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<LLMEvent(id={self.id}, model={self.model}, status={self.status})>"

