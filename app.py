"""
FastAPI server for EmailTriageEnv.
Exposes /reset, /step, /state, /tasks, /metadata, /schema, /mcp, /health endpoints.
Enhanced with analytics, leaderboards, and batch evaluation.
"""
import os
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from env import EmailTriageEnv, EmailAction
from env.analytics import get_tracker
from env.dataset import SCENARIOS

app = FastAPI(
    title="email-triage-env",
    description="OpenEnv environment: AI agent triages emails with advanced analytics",
    version="2.0.0",
)

# Enable CORS for web-based agents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_envs: dict = {}
_episode_tracking: dict = {}  # Track episode start times and actions


def get_env(task: str = "easy", scenario_index: int = 0) -> EmailTriageEnv:
    key = f"{task}_{scenario_index}"
    if key not in _envs:
        _envs[key] = EmailTriageEnv(task=task, scenario_index=scenario_index)
    return _envs[key]


class ResetRequest(BaseModel):
    task: Optional[str] = "easy"
    scenario_index: Optional[int] = 0
    agent_id: Optional[str] = "anonymous"


class StepRequest(BaseModel):
    action: str
    task: Optional[str] = "easy"
    scenario_index: Optional[int] = 0
    agent_id: Optional[str] = "anonymous"


class StateRequest(BaseModel):
    task: Optional[str] = "easy"
    scenario_index: Optional[int] = 0


class BatchEvalRequest(BaseModel):
    agent_id: str
    tasks: Optional[List[str]] = ["easy", "medium", "hard"]
    scenario_indices: Optional[Dict[str, List[int]]] = None


@app.get("/")
def root():
    return {
        "status": "ok",
        "env": "email-triage-env",
        "version": "2.0.0",
        "features": [
            "multi-scenario support",
            "analytics tracking",
            "leaderboard system",
            "batch evaluation",
            "performance metrics"
        ],
        "endpoints": {
            "core": ["/reset", "/step", "/state", "/tasks"],
            "analytics": ["/analytics/stats", "/analytics/leaderboard", "/analytics/agent/{agent_id}"],
            "info": ["/health", "/metadata", "/schema", "/scenarios"]
        }
    }


@app.get("/health")
def health():
    tracker = get_tracker()
    global_stats = tracker.get_global_stats()
    return {
        "status": "healthy",
        "uptime_seconds": global_stats.get("uptime_seconds", 0),
        "total_episodes": global_stats.get("total_episodes", 0),
        "unique_agents": global_stats.get("unique_agents", 0)
    }


@app.post("/reset")
def reset(req: ResetRequest = None):
    if req is None:
        req = ResetRequest()
    try:
        env = get_env(req.task or "easy", req.scenario_index or 0)
        result = env.reset()
        
        # Track episode start
        episode_key = f"{req.agent_id}_{req.task}_{req.scenario_index}_{time.time()}"
        _episode_tracking[episode_key] = {
            "agent_id": req.agent_id,
            "task": req.task,
            "scenario_index": req.scenario_index,
            "start_time": time.time(),
            "actions": [],
            "rewards": [],
        }
        
        response = result.model_dump()
        response["episode_key"] = episode_key
        return JSONResponse(content=response, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(req: StepRequest):
    try:
        env = get_env(req.task or "easy", req.scenario_index or 0)
        action = EmailAction(action=req.action)
        result = env.step(action)
        
        # Find active episode for this agent
        episode_key = None
        for key, tracking in _episode_tracking.items():
            if (tracking["agent_id"] == req.agent_id and 
                tracking["task"] == req.task and 
                tracking["scenario_index"] == req.scenario_index):
                episode_key = key
                break
        
        if episode_key:
            _episode_tracking[episode_key]["actions"].append(req.action)
            _episode_tracking[episode_key]["rewards"].append(result.reward)
            
            # If episode is done, record to analytics
            if result.done:
                tracking = _episode_tracking[episode_key]
                duration = time.time() - tracking["start_time"]
                state = env.state()
                
                tracker = get_tracker()
                tracker.record_episode(
                    agent_id=req.agent_id,
                    task=req.task,
                    scenario_id=state["scenario_id"],
                    score=state["best_grade"],
                    steps=len(tracking["actions"]),
                    success=state["best_grade"] >= 0.5,
                    duration=duration,
                    actions=tracking["actions"],
                    rewards=tracking["rewards"]
                )
                
                # Clean up tracking
                del _episode_tracking[episode_key]
        
        return JSONResponse(content=result.model_dump(), status_code=200)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/state")
def state(req: StateRequest = None):
    if req is None:
        req = StateRequest()
    env = get_env(req.task or "easy", req.scenario_index or 0)
    return JSONResponse(content=env.state(), status_code=200)


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"name": "easy", "description": "Single email: categorize and prioritize", "difficulty": "easy", "max_steps": 5, "reward_range": [0.0, 1.0], "grader": "deterministic"},
            {"name": "medium", "description": "Multiple emails: triage and prioritize", "difficulty": "medium", "max_steps": 5, "reward_range": [0.0, 1.0], "grader": "deterministic_partial_credit"},
            {"name": "hard", "description": "Complex escalation with legal risk", "difficulty": "hard", "max_steps": 5, "reward_range": [0.0, 1.0], "grader": "deterministic_partial_credit"},
        ]
    }


@app.get("/metadata")
def metadata():
    return {
        "name": "email-triage-env",
        "version": "1.0.0",
        "description": "OpenEnv environment: AI agent triages emails",
        "tags": ["openenv", "hackathon", "email-triage", "llm-agents"],
    }


@app.get("/schema")
def schema():
    return {
        "action": {"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]},
        "observation": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "step": {"type": "integer"},
                "max_steps": {"type": "integer"},
                "emails": {"type": "array"},
                "available_actions": {"type": "array"},
                "context": {"type": "string"},
                "last_action_result": {"type": ["string", "null"]},
                "last_action_error": {"type": ["string", "null"]},
            }
        }
    }


@app.post("/mcp")
async def mcp(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    return {"jsonrpc": "2.0", "id": body.get("id", 1), "result": {"method": body.get("method", "ping"), "status": "ok", "env": "email-triage-env"}}


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/analytics/stats")
def get_global_stats():
    """Get global environment statistics."""
    tracker = get_tracker()
    return tracker.get_global_stats()


@app.get("/analytics/agent/{agent_id}")
def get_agent_stats(agent_id: str):
    """Get detailed statistics for a specific agent."""
    tracker = get_tracker()
    stats = tracker.get_agent_stats(agent_id)
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    return stats


@app.get("/analytics/leaderboard")
def get_leaderboard(task: Optional[str] = None, limit: int = 10):
    """
    Get leaderboard rankings.
    
    Query params:
        task: Filter by specific task (easy/medium/hard)
        limit: Number of top agents to return (default: 10)
    """
    tracker = get_tracker()
    return {
        "task": task or "all",
        "limit": limit,
        "rankings": tracker.get_leaderboard(task=task, limit=limit)
    }


@app.get("/analytics/recent")
def get_recent_episodes(limit: int = 20, agent_id: Optional[str] = None):
    """
    Get recent episodes.
    
    Query params:
        limit: Number of episodes to return (default: 20)
        agent_id: Filter by specific agent
    """
    tracker = get_tracker()
    return {
        "episodes": tracker.get_recent_episodes(limit=limit, agent_id=agent_id)
    }


@app.get("/analytics/export")
def export_analytics():
    """Export all analytics data as JSON."""
    tracker = get_tracker()
    return JSONResponse(
        content=tracker.export_data(),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=analytics_export.json"}
    )


@app.get("/scenarios")
def list_scenarios():
    """List all available scenarios across all difficulty levels."""
    scenario_info = {}
    for task, scenarios in SCENARIOS.items():
        scenario_info[task] = {
            "count": len(scenarios),
            "scenarios": [
                {
                    "id": s["id"],
                    "context": s["context"],
                    "email_count": len(s["emails"]),
                    "action_count": len(s["available_actions"])
                }
                for s in scenarios
            ]
        }
    return scenario_info


@app.get("/scenarios/{task}/{index}")
def get_scenario_details(task: str, index: int):
    """Get detailed information about a specific scenario."""
    if task not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Task '{task}' not found")
    
    scenarios = SCENARIOS[task]
    if index < 0 or index >= len(scenarios):
        raise HTTPException(status_code=404, detail=f"Scenario index {index} out of range")
    
    return scenarios[index]


def main():
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
