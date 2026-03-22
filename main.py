from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import logging
import json
import time
from typing import AsyncGenerator


from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.agents.experimental.requirements.conditional import ConditionalRequirement
from beeai_framework.agents.experimental.requirements.ask_permission import AskPermissionRequirement
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.backend import ChatModel, ChatModelParameters
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.weather import OpenMeteoTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool


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
    Advanced Multi-Agent Travel Planning System with Language Expert
    
    This system demonstrates:
    1. Specialized agent roles and coordination
    2. Tool-based inter-agent communication
    3. Requirements-based execution control
    4. Language and cultural expertise integration
    5. Comprehensive travel planning workflow
    """
    
    # Initialize the language model
    llm = ChatModel.from_name(
        "watsonx:meta-llama/llama-4-maverick-17b-128e-instruct-fp8", 
        ChatModelParameters(temperature=0)
    )
    
    # === AGENT 1: DESTINATION RESEARCH EXPERT ===
    destination_expert = RequirementAgent(
        llm=llm,
        tools=[WikipediaTool(), ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are a Destination Research Expert specializing in comprehensive travel destination analysis.

        Your expertise:
        - Landmarks and tourist activities
        - Best times to visit and seasonal considerations
        - Transportation options and accessibility
        - Safety considerations and travel advisories

        Always provide detailed, factual information with clear source attribution.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=5,
                consecutive_allowed=False
            ),
            ConditionalRequirement(
                WikipediaTool,
                only_after=[ThinkTool],
                min_invocations=1,
                max_invocations=4,
                consecutive_allowed=False
            ),
        ]
    )
    
    # === AGENT 2: TRAVEL METEOROLOGIST ===
    travel_meteorologist = RequirementAgent(
        llm=llm,
        tools=[OpenMeteoTool(), ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are a Travel Meteorologist specializing in weather analysis for travel planning.

        Your expertise:
        - Climate patterns and seasonal weather analysis
        - Travel-specific weather recommendations
        - Packing suggestions based on weather forecasts
        - Activity planning based on weather conditions
        - Regional climate variations and microclimates
        - Weather-related travel risks and precautions

        Focus on actionable weather guidance for travelers.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=2
            ),
            ConditionalRequirement(
                OpenMeteoTool,
                only_after=[ThinkTool],
                min_invocations=1,
                max_invocations=1
            )
        ]
    )
    
    # === AGENT 3: LANGUAGE & CULTURAL EXPERT ===
    language_and_culture_expert = RequirementAgent(
        llm=llm,
        tools=[WikipediaTool(), ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are a Language & Cultural Expert specializing in linguistic and cultural guidance for travelers.

        Your expertise:
        - Local languages and dialects spoken in destinations
        - Essential phrases and communication tips for travelers
        - Cultural etiquette, customs, and social norms
        - Religious and cultural sensitivities to be aware of
        - Local communication styles and business etiquette
        - Cultural festivals, events, and local celebrations
        - Dining customs, tipping practices, and social interactions

        Always emphasize cultural sensitivity and respectful travel practices.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=3,
                consecutive_allowed=False
            ),
        ]
    )
    
    # === AGENT 4: TRAVEL COORDINATOR (MAIN INTERFACE) ===
    # Create handoff tools for coordination with unique names
    handoff_to_destination = HandoffTool(
        destination_expert,
        name="DestinationResearch",
        description="Consult our Destination Research Expert for comprehensive information about travel destinations, attractions, and practical travel guidance."
    )
    handoff_to_weather = HandoffTool(
        travel_meteorologist,
        name="WeatherPlanning", 
        description="Consult our Travel Meteorologist for weather forecasts, climate analysis, and weather-appropriate travel recommendations."
    )
    handoff_to_language = HandoffTool(
        language_and_culture_expert,
        name="LanguageCulturalGuidance",
        description="Consult our Language & Cultural Expert for essential phrases, cultural etiquette, and communication guidance for respectful travel."
    )
    
    travel_coordinator = RequirementAgent(
        llm=llm,
        tools=[handoff_to_destination, handoff_to_weather, handoff_to_language, ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are the Travel Coordinator, the main interface for comprehensive travel planning.

        Your role:
        - Understand traveler requirements and preferences
        - Coordinate with specialized expert agents as needed
        - Synthesize information from multiple sources
        - Create comprehensive, actionable travel recommendations
        - Ensure all aspects of travel planning are covered

        Available Expert Agents:
        - Destination Expert: Practical destination information
        - Travel Meteorologist: Weather analysis and climate recommendations  
        - Language Expert: Language tips, cultural etiquette, and communication guidance

        Coordination Process:
        1. Think about what information is needed for comprehensive travel planning
        2. Delegate specific queries to appropriate expert agents using handoff tools
        3. Gather insights from multiple specialists
        4. Synthesize information into cohesive travel recommendations
        5. Provide a complete travel planning summary

        Always ensure travelers receive well-rounded guidance covering destinations and landmarks, weather, and cultural considerations.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(ThinkTool, consecutive_allowed=False),
            AskPermissionRequirement(["DestinationResearch", "WeatherPlanning", "LanguageCulturalGuidance"])
        ]
    )


async def run_agent_pipeline(query: str) -> AsyncGenerator[str, None]:
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
        pass  
    except Exception as exc:
        yield sse("error", "System", str(exc))
        return


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
