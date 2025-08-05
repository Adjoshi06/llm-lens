# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

## Quick Start with Docker

1. **Start all services**:
   ```bash
   docker-compose up
   ```

2. **Access the dashboard**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **Run the demo script** (in a new terminal):
   ```bash
   cd examples
   PYTHONPATH=.. python demo.py
   ```

   On Windows:
   ```powershell
   cd examples
   $env:PYTHONPATH=".."
   python demo.py
   ```

4. **View the dashboard** to see the logged events!

## Manual Setup (Alternative)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev
```

### Database

```bash
docker run -d \
  --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=llm_monitor \
  timescale/timescaledb:latest-pg15
```

## Using the SDK

```python
from app.monitor.sdk import LLMMonitor

# Initialize monitor
monitor = LLMMonitor(api_url="http://localhost:8000")

# Track LLM calls with decorator
@monitor.track(tags={"user_id": "123", "feature": "chat"})
def my_llm_call():
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    return response

# Or manually log events
monitor.log_event(
    model="gpt-4",
    prompt_tokens=100,
    completion_tokens=50,
    total_tokens=150,
    latency_ms=850,
    status="success",
    tags={"user_id": "123"}
)
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Make sure PostgreSQL is running
2. Check the DATABASE_URL environment variable
3. Verify the database credentials

### Frontend Not Loading

If the frontend shows errors:
1. Check that the backend is running on port 8000
2. Verify NEXT_PUBLIC_API_URL is set correctly
3. Check browser console for errors

### Docker Issues

If Docker Compose fails:
1. Make sure Docker is running
2. Check if ports 3000, 8000, and 5432 are available
3. Try rebuilding: `docker-compose up --build`

## Next Steps

- Check the [README.md](README.md) for detailed documentation
- View the [examples/demo.py](examples/demo.py) for SDK usage examples
- Explore the API documentation at http://localhost:8000/docs

