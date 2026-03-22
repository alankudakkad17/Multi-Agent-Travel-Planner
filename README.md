# Travel Planner — Multi-Agent Full-Stack App

An AI-powered travel planning application that utilizes specialized expert agents (Destination, Weather, Language, and Coordinator) to synthesize real-time travel recommendations.

## Architecture

All files are currently located in the root directory:

```
App.jsx            ← React frontend main UI component
main.py            ← FastAPI backend server running BeeAI agents
requirements.txt   ← Python dependencies
```

## Backend Setup

Install the required Python dependencies and start the FastAPI server:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

The backend is configured to use the `beeai_framework` and stream Server-Sent Events (SSE) detailing the trajectory of the agents' thought processes.

## Frontend Setup

Since `App.jsx` is a single React component, you will need to scaffold a React environment if you haven't already:

```bash
# Create a new Vite project (if needed)
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Move the App.jsx into the source folder
mv ../App.jsx src/App.jsx

# Start the development server
npm run dev   # → http://localhost:5173
```

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
