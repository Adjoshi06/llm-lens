# LLM Monitor - Monitoring & Observability Dashboard (MVP)

A minimal viable product for monitoring LLM API calls (OpenAI, Anthropic) with a real-time web dashboard.

## Features

- **Real-time Monitoring**: Track LLM API calls with metrics, costs, and latency
- **Dashboard**: Clean, modern web interface with charts and statistics
- **Python SDK**: Simple decorator-based monitoring wrapper
- **Cost Tracking**: Automatic cost calculation based on token usage and model pricing
- **Time-Series Analytics**: View metrics over time with interactive charts
- **Error Tracking**: Monitor failed API calls and error rates

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with TimescaleDB extension
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Visualization**: Recharts
- **Deployment**: Docker Compose for local development

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Running with Docker Compose

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Start all services**:
   ```bash
   docker-compose up
   ```

3. **Access the services**:
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Manual Setup (Local Development)

#### Backend

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor"
   ```

5. **Start the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set environment variables**:
   ```bash
   export NEXT_PUBLIC_API_URL="http://localhost:8000"
   ```

4. **Start the frontend**:
   ```bash
   npm run dev
   ```

#### Database

1. **Start PostgreSQL with TimescaleDB**:
   ```bash
   docker run -d \
     --name timescaledb \
     -p 5432:5432 \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=llm_monitor \
     timescale/timescaledb:latest-pg15
   ```

2. **Initialize the database** (tables will be created automatically on first run)

## Usage

### Python SDK

#### Basic Usage

```python
from app.monitor.sdk import LLMMonitor

# Initialize monitor
monitor = LLMMonitor(api_url="http://localhost:8000")

# Use decorator to track LLM calls
@monitor.track(tags={"user_id": "123", "feature": "chat"})
def my_llm_call():
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    return response

# Call the function
result = my_llm_call()
```

#### Manual Event Logging

```python
monitor.log_event(
    model="gpt-4",
    prompt_tokens=100,
    completion_tokens=50,
    total_tokens=150,
    latency_ms=850,
    status="success",
    tags={"user_id": "123", "feature": "chat"}
)
```

#### Error Tracking

```python
@monitor.track(tags={"user_id": "123"})
def my_llm_call():
    try:
        response = openai.chat.completions.create(...)
        return response
    except Exception as e:
        # Error will be automatically logged by the decorator
        raise
```

### Running the Demo

```bash
# Make sure backend is running
cd examples
python demo.py
```

## API Endpoints

### POST /api/events

Log a new LLM event.

**Request Body**:
```json
{
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
```

### GET /api/metrics/overview

Get dashboard overview metrics.

**Query Parameters**:
- `hours` (optional): Number of hours to look back (default: 24)

**Response**:
```json
{
  "total_requests": 1234,
  "total_cost": 45.67,
  "avg_latency_ms": 850,
  "error_rate": 2.3,
  "requests_by_model": {"gpt-4": 800, "claude-sonnet-4": 434}
}
```

### GET /api/metrics/timeseries

Get time-series data for charts.

**Query Parameters**:
- `start_time`: Start time (ISO format)
- `end_time`: End time (ISO format)
- `interval`: Time interval (`1h` or `1d`)
- `metric`: Metric to query (`requests`, `cost`, or `latency`)
- `model` (optional): Filter by model

### GET /api/conversations

Get recent LLM calls with pagination.

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 100)
- `model` (optional): Filter by model
- `status` (optional): Filter by status (`success` or `error`)

## Dashboard

The dashboard provides:

1. **Stats Cards**: Total requests, cost, average latency, and error rate
2. **Metrics Chart**: Interactive line chart showing requests, cost, or latency over time
3. **Cost Tracker**: Pie chart and table showing cost breakdown by model
4. **Recent Calls**: Table of recent LLM API calls with expandable details

## Pricing

The system includes pricing tables for common models:

- **GPT-4**: $30/1M input, $60/1M output
- **GPT-4 Mini**: $0.15/1M input, $0.60/1M output
- **Claude Sonnet 4**: $3/1M input, $15/1M output

Costs are automatically calculated based on token usage. See `backend/app/monitor/pricing.py` for the complete pricing table.

## Project Structure

```
llm-monitor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # DB connection
│   │   ├── routers/
│   │   │   ├── events.py        # Log LLM events
│   │   │   ├── metrics.py       # Query metrics
│   │   │   └── conversations.py # View conversations
│   │   └── monitor/
│   │       ├── sdk.py           # Python SDK wrapper
│   │       └── pricing.py       # Pricing tables
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Dashboard home
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── MetricsChart.tsx
│   │   ├── CostTracker.tsx
│   │   ├── RecentCalls.tsx
│   │   └── StatsCard.tsx
│   ├── lib/
│   │   └── api.ts               # API client
│   ├── package.json
│   └── Dockerfile
├── examples/
│   └── demo.py                  # Demo script
├── docker-compose.yml
└── README.md
```

## Environment Variables

### Backend

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor`)

### Frontend

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## Database Schema

### llm_events

- `id`: UUID primary key
- `timestamp`: Event timestamp (indexed, used for TimescaleDB hypertable)
- `model`: Model name (indexed)
- `prompt_tokens`: Number of input tokens
- `completion_tokens`: Number of output tokens
- `total_tokens`: Total number of tokens
- `latency_ms`: Latency in milliseconds
- `cost_usd`: Cost in USD
- `status`: Status (`success` or `error`, indexed)
- `error_message`: Error message (if failed)
- `tags`: JSONB field for custom metadata
- `created_at`: Record creation timestamp

### TimescaleDB

The `llm_events` table is converted to a TimescaleDB hypertable for optimized time-series queries. Continuous aggregates are created for hourly metrics.

## Limitations (MVP)

- No authentication (add later)
- No real-time WebSocket updates (polling every 30 seconds)
- No advanced alerting (can add later)
- No prompt versioning yet (future feature)
- Hardcoded pricing tables (no admin UI yet)
- Support only OpenAI and Anthropic initially
- 30-day data retention (auto-cleanup old data - not implemented yet)

## Future Enhancements

- Authentication and authorization
- Real-time WebSocket updates
- Advanced alerting and notifications
- Prompt versioning and tracking
- Admin UI for managing pricing tables
- Support for more LLM providers
- Data retention policies
- Export functionality
- Custom dashboards
- Team collaboration features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

