from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import logging
import json
import time
from typing import AsyncGenerator

# ── Uncomment these when beeai_framework is installed ──────────────────────────
# from beeai_framework.agents.experimental import RequirementAgent
# from beeai_framework.agents.experimental.requirements.conditional import ConditionalRequirement
# from beeai_framework.agents.experimental.requirements.ask_permission import AskPermissionRequirement
# from beeai_framework.memory import UnconstrainedMemory
# from beeai_framework.backend import ChatModel, ChatModelParameters
# from beeai_framework.tools.search.wikipedia import WikipediaTool
# from beeai_framework.tools.weather import OpenMeteoTool
# from beeai_framework.tools.think import ThinkTool
# from beeai_framework.tools.handoff import HandoffTool
# from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
# from beeai_framework.tools import Tool
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Travel Planner Multi-Agent API",
    description="AI-powered travel planning with specialized expert agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ──────────────────────────────────────────────────

class TravelQuery(BaseModel):
    query: str
    destinations: list[str] = []
    duration_days: int = 7
    traveler_type: str = "first-time"


class AgentEvent(BaseModel):
    event: str          # "agent_start" | "agent_thinking" | "tool_call" | "agent_done" | "final_result" | "error"
    agent: str
    message: str
    data: dict = {}
    timestamp: float = 0.0


# ── Agent pipeline ─────────────────────────────────────────────────────────────

def build_agents():
    """
    Build and return the multi-agent pipeline.
    Replace the stub below with actual BeeAI agent construction once the
    framework is installed.
    """
    # llm = ChatModel.from_name(
    #     "watsonx:meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
    #     ChatModelParameters(temperature=0)
    # )
    # … (same construction as t12.py) …
    # return travel_coordinator
    raise NotImplementedError("BeeAI framework not installed – using mock pipeline")


async def run_agent_pipeline(query: str) -> AsyncGenerator[str, None]:
    """
    Runs the multi-agent travel-planning pipeline and streams Server-Sent Events
    back to the client.

    In production: replace the mock sequence with actual agent invocations and
    forward real trajectory events from GlobalTrajectoryMiddleware.
    """

    def sse(event: str, agent: str, message: str, data: dict = {}) -> str:
        payload = {
            "event": event,
            "agent": agent,
            "message": message,
            "data": data,
            "timestamp": time.time(),
        }
        return f"data: {json.dumps(payload)}\n\n"

    # ── Attempt real pipeline ──────────────────────────────────────────────────
    try:
        coordinator = build_agents()
        result = await coordinator.run(query)
        yield sse("final_result", "Travel Coordinator", result.answer.text)
        return
    except NotImplementedError:
        pass  # fall through to mock
    except Exception as exc:
        yield sse("error", "System", str(exc))
        return

    # ── Mock pipeline (illustrative) ──────────────────────────────────────────
    mock_steps = [
        ("agent_start",    "Travel Coordinator",  "Analyzing your travel request…",              {}),
        ("agent_thinking", "Travel Coordinator",  "Identifying required specialist consultations…", {}),
        ("tool_call",      "Travel Coordinator",  "Delegating to Destination Research Expert",   {"tool": "DestinationResearch"}),
        ("agent_start",    "Destination Expert",  "Researching Tokyo & Osaka…",                  {}),
        ("tool_call",      "Destination Expert",  "Searching Wikipedia for Tokyo attractions",   {"tool": "WikipediaTool", "query": "Tokyo tourist attractions"}),
        ("tool_call",      "Destination Expert",  "Searching Wikipedia for Osaka culture",       {"tool": "WikipediaTool", "query": "Osaka cultural sites"}),
        ("agent_done",     "Destination Expert",  "Destination research complete",               {"highlights": ["Senso-ji Temple", "Fushimi Inari Shrine", "Dotonbori", "teamLab Borderless"]}),
        ("tool_call",      "Travel Coordinator",  "Delegating to Travel Meteorologist",          {"tool": "WeatherPlanning"}),
        ("agent_start",    "Travel Meteorologist","Fetching climate data for Japan…",            {}),
        ("tool_call",      "Travel Meteorologist","Querying OpenMeteo for Tokyo weather",        {"tool": "OpenMeteoTool", "location": "Tokyo"}),
        ("tool_call",      "Travel Meteorologist","Querying OpenMeteo for Osaka weather",        {"tool": "OpenMeteoTool", "location": "Osaka"}),
        ("agent_done",     "Travel Meteorologist","Weather analysis complete",                   {"summary": "Mild temperatures 15-22°C, low rain probability. Light layers recommended."}),
        ("tool_call",      "Travel Coordinator",  "Delegating to Language & Cultural Expert",   {"tool": "LanguageCulturalGuidance"}),
        ("agent_start",    "Language Expert",     "Compiling cultural & language guidance…",    {}),
        ("tool_call",      "Language Expert",     "Researching Japanese etiquette",             {"tool": "WikipediaTool", "query": "Japanese customs etiquette tourists"}),
        ("agent_done",     "Language Expert",     "Cultural guidance ready",                    {"phrases": ["Sumimasen (Excuse me)", "Arigatou gozaimasu (Thank you)", "Eigo ga hanasemasu ka? (Do you speak English?)"]}),
        ("agent_thinking", "Travel Coordinator",  "Synthesizing insights from all specialists…", {}),
        ("final_result",   "Travel Coordinator",
         """🗾 **Your 2-Week Japan Cultural Immersion Plan**

**DESTINATIONS**
Tokyo (Days 1–9) and Osaka (Days 10–14) offer a perfect contrast of modern metropolis and historic heart of Japan.

**TOP EXPERIENCES**
• Senso-ji Temple (Asakusa) – Tokyo's oldest Buddhist temple; arrive at dawn
• teamLab Borderless – Immersive digital art in Odaiba
• Fushimi Inari Shrine – 10,000 vermillion torii gates; hike early morning
• Dotonbori – Osaka's neon-lit foodie paradise
• Osaka Castle – Feudal history with panoramic city views
• Nishiki Market – "Kyoto's Kitchen" day-trip from Osaka

**WEATHER (April/May ideal)**
Temperatures: 15–22 °C in Tokyo, 17–24 °C in Osaka
Expect cherry blossoms in early April. Pack light layers and a compact umbrella.

**LANGUAGE & CULTURAL TIPS**
• Bow slightly when greeting – depth reflects formality
• Remove shoes before entering traditional spaces (look for the step/mat)
• No tipping – it can be considered rude
• Speak quietly on public transport; phone calls are discouraged
• Key phrases: Sumimasen (すみません) · Arigatou gozaimasu · Eigo ga hanasemasu ka?
• IC card (Suica/ICOCA) covers trains, buses, and convenience store payments

**PRACTICAL NOTES**
• JR Pass (14-day) covers bullet-train travel between cities
• Pocket Wi-Fi or eSIM essential for navigation
• Most major attractions accept cards; carry cash for smaller shrines & markets""",
         {}),
    ]

    for event, agent, message, data in mock_steps:
        yield sse(event, agent, message, data)
        await asyncio.sleep(0.7)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "travel-planner-api"}


@app.post("/plan/stream")
async def plan_stream(body: TravelQuery):
    """Stream agent events as Server-Sent Events."""
    full_query = body.query
    if body.destinations:
        full_query += f" Destinations: {', '.join(body.destinations)}."
    if body.duration_days:
        full_query += f" Duration: {body.duration_days} days."
    if body.traveler_type:
        full_query += f" Traveler type: {body.traveler_type}."

    return StreamingResponse(
        run_agent_pipeline(full_query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/plan")
async def plan_sync(body: TravelQuery):
    """Non-streaming endpoint – collects all events and returns the final result."""
    full_query = body.query
    events = []
    final_text = ""

    async for raw in run_agent_pipeline(full_query):
        if raw.startswith("data: "):
            payload = json.loads(raw[6:])
            events.append(payload)
            if payload["event"] == "final_result":
                final_text = payload["message"]

    return {"result": final_text, "events": events}
