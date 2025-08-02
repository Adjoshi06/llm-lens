"""
Router for querying metrics and analytics.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, case, and_
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import get_db
from app.models import LLMEvent
from app.schemas import MetricsOverviewResponse, TimeSeriesResponse, TimeSeriesDataPoint

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview", response_model=MetricsOverviewResponse)
async def get_metrics_overview(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview metrics for the dashboard.
    
    Returns total requests, total cost, average latency, error rate, and requests by model
    for the specified time period (default: last 24 hours).
    """
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Build query for metrics
        query = select(
            func.count(LLMEvent.id).label("total_requests"),
            func.coalesce(func.sum(LLMEvent.cost_usd), 0).label("total_cost"),
            func.coalesce(func.avg(LLMEvent.latency_ms), 0).label("avg_latency"),
            func.sum(case((LLMEvent.status == "error", 1), else_=0)).label("error_count")
        ).where(
            and_(
                LLMEvent.timestamp >= start_time,
                LLMEvent.timestamp <= end_time
            )
        )
        
        result = await db.execute(query)
        metrics = result.first()
        
        # Get requests by model
        model_query = select(
            LLMEvent.model,
            func.count(LLMEvent.id).label("count")
        ).where(
            and_(
                LLMEvent.timestamp >= start_time,
                LLMEvent.timestamp <= end_time
            )
        ).group_by(LLMEvent.model)
        
        model_result = await db.execute(model_query)
        requests_by_model = {row.model: row.count for row in model_result}
        
        # Calculate error rate
        total_requests = metrics.total_requests or 0
        error_count = metrics.error_count or 0
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
        
        return MetricsOverviewResponse(
            total_requests=total_requests,
            total_cost=float(metrics.total_cost or 0),
            avg_latency_ms=float(metrics.avg_latency or 0),
            error_rate=round(error_rate, 2),
            requests_by_model=requests_by_model
        )
        
    except Exception as e:
        logger.error(f"Error getting metrics overview: {e}", exc_info=True)
        raise


@router.get("/timeseries", response_model=TimeSeriesResponse)
async def get_timeseries(
    start_time: datetime = Query(..., description="Start time (ISO format)"),
    end_time: datetime = Query(..., description="End time (ISO format)"),
    interval: str = Query("1h", regex="^(1h|1d)$", description="Time interval (1h or 1d)"),
    metric: str = Query("requests", regex="^(requests|cost|latency)$", description="Metric to query"),
    model: Optional[str] = Query(None, description="Filter by model (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get time-series data for charts.
    
    Returns data points for the specified metric over the given time range.
    """
    try:
        # Determine bucket size based on interval
        if interval == "1h":
            trunc_unit = "hour"
        else:
            trunc_unit = "day"
        
        # Build query based on metric
        if metric == "requests":
            value_expr = func.count(LLMEvent.id)
        elif metric == "cost":
            value_expr = func.coalesce(func.sum(LLMEvent.cost_usd), 0)
        elif metric == "latency":
            value_expr = func.coalesce(func.avg(LLMEvent.latency_ms), 0)
        else:
            value_expr = func.count(LLMEvent.id)
        
        # Build base query with date_trunc
        query = select(
            func.date_trunc(trunc_unit, LLMEvent.timestamp).label("bucket"),
            LLMEvent.model,
            value_expr.label("value")
        ).where(
            and_(
                LLMEvent.timestamp >= start_time,
                LLMEvent.timestamp <= end_time
            )
        ).group_by(
            func.date_trunc(trunc_unit, LLMEvent.timestamp),
            LLMEvent.model
        ).order_by(
            func.date_trunc(trunc_unit, LLMEvent.timestamp),
            LLMEvent.model
        )
        
        # Add model filter if provided
        if model:
            query = query.where(LLMEvent.model == model)
        
        result = await db.execute(query)
        rows = result.all()
        
        # Convert to response format
        data = [
            TimeSeriesDataPoint(
                timestamp=row.bucket,
                value=float(row.value),
                model=row.model
            )
            for row in rows
        ]
        
        return TimeSeriesResponse(data=data)
        
    except Exception as e:
        logger.error(f"Error getting timeseries data: {e}", exc_info=True)
        raise

