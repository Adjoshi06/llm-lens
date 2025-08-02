"""
Database connection and session management.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables and TimescaleDB hypertable."""
    # Import models to ensure they're registered with Base.metadata
    from app import models  # noqa: F401
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Check if TimescaleDB extension is available and create hypertable
        try:
            # Enable TimescaleDB extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # Convert llm_events to hypertable if it doesn't exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM _timescaledb_catalog.hypertable 
                    WHERE hypertable_name = 'llm_events'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                await conn.execute(text("""
                    SELECT create_hypertable('llm_events', 'timestamp', 
                                           if_not_exists => TRUE);
                """))
                logger.info("Created TimescaleDB hypertable for llm_events")
            else:
                logger.info("Hypertable llm_events already exists")
        except Exception as e:
            logger.warning(f"TimescaleDB setup failed (this is ok if extension is not available): {e}")
        
        # Create continuous aggregate view for hourly metrics
        try:
            await conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS llm_metrics_hourly
                WITH (timescaledb.continuous) AS
                SELECT
                    time_bucket('1 hour', timestamp) AS bucket,
                    model,
                    COUNT(*) as request_count,
                    SUM(cost_usd) as total_cost,
                    AVG(latency_ms) as avg_latency,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
                FROM llm_events
                GROUP BY bucket, model;
            """))
            logger.info("Created continuous aggregate view llm_metrics_hourly")
        except Exception as e:
            logger.warning(f"Continuous aggregate view creation failed: {e}")

