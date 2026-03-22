# Travel Planner — Multi-Agent Full-Stack App

## Architecture

```
frontend/  (React + Vite)
  src/App.jsx        ← main UI component

backend/
  main.py            ← FastAPI server (wraps t12.py agents)
  requirements.txt
```

## Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

### Connecting BeeAI agents
In `main.py`, find `build_agents()` and replace the stub with the agent
construction from your original `t12.py`. The SSE stream in
`run_agent_pipeline()` should forward real trajectory events from
`GlobalTrajectoryMiddleware` — replace the mock steps list with actual
`await coordinator.run(query)` calls and yield SSE events from the middleware.

## Frontend Setup

```bash
cd frontend
npm create vite@latest . -- --template react   # first time only
npm install
npm run dev   # → http://localhost:5173
```

Replace `src/App.jsx` with the provided file (or copy it in).

## API Endpoints

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| GET    | /health        | Health check                             |
| POST   | /plan/stream   | **SSE stream** of agent events           |
| POST   | /plan          | Sync endpoint, returns full JSON result  |

### Request body (`/plan/stream` and `/plan`)
```json
{
  "query": "I want to visit Japan for 2 weeks...",
  "destinations": ["Tokyo", "Osaka"],
  "duration_days": 14,
  "traveler_type": "first-time"
}
```

### SSE event shape
```json
{
  "event": "agent_start | agent_thinking | tool_call | agent_done | final_result | error",
  "agent": "Travel Coordinator",
  "message": "Human-readable description",
  "data": {},
  "timestamp": 1712345678.123
}
```
