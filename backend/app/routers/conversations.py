"""
Router for viewing conversations and recent LLM calls.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional
import logging

from app.database import get_db
from app.models import LLMEvent
from app.schemas import ConversationsResponse, LLMEventResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/conversations", response_model=ConversationsResponse)
async def get_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of items per page"),
    model: Optional[str] = Query(None, description="Filter by model"),
    status: Optional[str] = Query(None, regex="^(success|error)$", description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent LLM API calls with pagination.
    
    Returns a paginated list of events, ordered by timestamp (newest first).
    """
    try:
        # Build query
        query = select(LLMEvent)
        count_query = select(func.count(LLMEvent.id))
        
        # Apply filters
        if model:
            query = query.where(LLMEvent.model == model)
            count_query = count_query.where(LLMEvent.model == model)
        
        if status:
            query = query.where(LLMEvent.status == status)
            count_query = count_query.where(LLMEvent.status == status)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(desc(LLMEvent.timestamp)).offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        events = result.scalars().all()
        
        return ConversationsResponse(
            events=events,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}", exc_info=True)
        raise

