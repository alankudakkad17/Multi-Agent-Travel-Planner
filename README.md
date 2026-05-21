# Travel Planner — Multi-Agent Full-Stack App

An AI-powered travel planning application that uses 4 specialized expert agents (Destination, Weather, Language, and Coordinator) to synthesize real-time travel recommendations via Server-Sent Events.

## Project Structure

```
├── backend/
│   ├── main.py            ← FastAPI server + BeeAI agent pipeline
│   ├── requirements.txt   ← Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx        ← Main React UI component
│   │   └── main.jsx       ← React entry point
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── nginx.conf         ← Production nginx config
│   ├── .env.example       ← Frontend env template
│   └── Dockerfile
├── .env.example           ← Root env template (WatsonX credentials)
├── .gitignore
└── docker-compose.yml
```

## Quick Start (Docker)

```bash
# 1. Copy the env template and fill in your WatsonX credentials
cp .env.example .env

# 2. Build and start both services
docker compose up --build

# Frontend → http://localhost:3000
# Backend  → http://localhost:8000
```

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export WATSONX_API_KEY=your_key
export WATSONX_PROJECT_ID=your_project_id
export WATSONX_URL=https://us-south.ml.cloud.ibm.com

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Copy and configure env
cp .env.example .env

npm run dev   # → http://localhost:5173
```

> The Vite dev server proxies `/plan` and `/health` to `http://localhost:8000` automatically — no CORS issues during development.

## Environment Variables

### Root `.env` (backend + Docker)

| Variable | Required | Default | Description |
|---|---|---|---|
| `WATSONX_API_KEY` | Yes | — | IBM WatsonX API key |
| `WATSONX_PROJECT_ID` | Yes | — | IBM WatsonX project ID |
| `WATSONX_URL` | No | `https://us-south.ml.cloud.ibm.com` | WatsonX regional endpoint |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:5173` | Comma-separated allowed origins |
| `VITE_API_BASE` | No | `http://localhost:8000` | API URL baked into Docker frontend build |

### `frontend/.env`

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE` | `http://localhost:8000` | Backend URL used by the browser |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/plan/stream` | SSE stream of agent events |
| POST | `/plan` | Sync endpoint, returns full JSON result |

### Request body

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

## Agent Architecture

```
Travel Coordinator (orchestrator)
├── DestinationResearch  →  Destination Expert   (WikipediaTool, ThinkTool)
├── WeatherPlanning      →  Travel Meteorologist  (OpenMeteoTool, ThinkTool)
└── LanguageCulturalGuidance → Language Expert   (WikipediaTool, ThinkTool)
```
