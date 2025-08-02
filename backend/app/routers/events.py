"""
Router for logging LLM events.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import LLMEvent
from app.schemas import LLMEventCreate, LLMEventResponse
from app.monitor.pricing import calculate_cost

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/events", response_model=LLMEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: LLMEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Log a new LLM API call event.
    
    If cost_usd is not provided, it will be calculated based on tokens and model pricing.
    """
    try:
        # Calculate cost if not provided
        if event.cost_usd is None:
            event.cost_usd = calculate_cost(
                model=event.model,
                prompt_tokens=event.prompt_tokens or 0,
                completion_tokens=event.completion_tokens or 0
            )
        
        # Create event
        db_event = LLMEvent(
            timestamp=event.timestamp,
            model=event.model,
            prompt_tokens=event.prompt_tokens,
            completion_tokens=event.completion_tokens,
            total_tokens=event.total_tokens,
            latency_ms=event.latency_ms,
            cost_usd=event.cost_usd,
            status=event.status,
            error_message=event.error_message,
            tags=event.tags
        )
        
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        
        logger.info(f"Logged LLM event: {db_event.id} - {db_event.model} - {db_event.status}")
        
        return db_event
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )

