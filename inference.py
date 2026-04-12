"""
Inference script for EmailTriageEnv with analytics integration.
Tests all scenarios and displays performance metrics.

Required env vars:
  API_BASE_URL   - LLM endpoint (default: https://router.huggingface.co/v1)
  MODEL_NAME     - model identifier (default: Qwen/Qwen2.5-72B-Instruct)
  HF_TOKEN       - Hugging Face / API key
  AGENT_ID       - Unique identifier for this agent (optional)
  EVAL_MODE      - "quick" (1 scenario/task) or "full" (all scenarios) (default: quick)
"""
import os
import json
import urllib.request
from typing import List, Optional, Dict, Any
from openai import OpenAI

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:7860")
AGENT_ID = os.getenv("AGENT_ID", f"agent_{MODEL_NAME.replace('/', '_')}")
EVAL_MODE = os.getenv("EVAL_MODE", "quick")  # "quick" or "full"
BENCHMARK = "email-triage-env"
TASKS = ["easy", "medium", "hard"]
MAX_STEPS = {"easy": 5, "medium": 5, "hard": 5}
SUCCESS_THRESHOLD = 0.5


def log_start(task: str, scenario_index: int, env: str, model: str) -> None:
    print(f"[START] task={task} scenario={scenario_index} env={env} model={model} agent_id={AGENT_ID}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    action_clean = action.replace("\n", " ")[:200]
    print(f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def _post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{SERVER_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _get(path: str) -> dict:
    req = urllib.request.Request(f"{SERVER_URL}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def env_reset(task: str, scenario_index: int = 0) -> dict:
    return _post("/reset", {"task": task, "scenario_index": scenario_index, "agent_id": AGENT_ID})


def env_step(task: str, action: str, scenario_index: int = 0) -> dict:
    return _post("/step", {"task": task, "action": action, "scenario_index": scenario_index, "agent_id": AGENT_ID})


def env_state(task: str, scenario_index: int = 0) -> dict:
    return _post("/state", {"task": task, "scenario_index": scenario_index})


def get_scenarios() -> dict:
    """Fetch available scenarios from server."""
    try:
        return _get("/scenarios")
    except Exception:
        return {task: {"count": 1} for task in TASKS}


def get_agent_stats() -> dict:
    """Fetch agent statistics from server."""
    try:
        return _get(f"/analytics/agent/{AGENT_ID}")
    except Exception:
        return {"error": "No stats available yet"}


def get_leaderboard(task: Optional[str] = None) -> dict:
    """Fetch leaderboard from server."""
    try:
        path = "/analytics/leaderboard"
        if task:
            path += f"?task={task}"
        return _get(path)
    except Exception:
        return {"rankings": []}


SYSTEM_PROMPT = """You are an expert email triage specialist with years of experience in corporate communications.
You will receive emails and must respond with exactly one action string from the available_actions list.

Rules:
- Reply with ONLY the action string — no explanation, no markdown, no extra text.
- The action must be exactly one of the available_actions listed in the observation.
- For easy tasks: pick the action matching the correct category, priority, and suggested action.
- For medium tasks: pick the action with the correct priority order and immediate actions.
- For hard tasks: pick the action with the correct escalation path and strategy.

Consider:
- Urgency indicators (URGENT, time-sensitive language)
- Sender importance (VIP, executive, regulatory)
- Risk factors (legal, security, financial)
- Business impact (revenue, reputation, compliance)
"""


def build_prompt(obs: dict) -> str:
    emails_text = "\n".join(
        f"  Email {i+1}: From: {e.get('from','?')} | Subject: {e.get('subject','?')} | Body: {e.get('body','?')[:200]}"
        for i, e in enumerate(obs["emails"])
    )
    actions_text = "\n".join(f"  - {a}" for a in obs["available_actions"])
    return f"""Task: {obs['task']}
Step: {obs['step']} / {obs['max_steps']}

EMAILS:
{emails_text}

CONTEXT:
{obs['context']}

AVAILABLE ACTIONS:
{actions_text}

Your action:"""


def get_agent_action(client: OpenAI, obs: dict) -> str:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(obs)}
            ],
            temperature=0.0,
            max_tokens=150,
        )
        text = (completion.choices[0].message.content or "").strip().split("\n")[0].strip()
        return text if text in obs["available_actions"] else obs["available_actions"][0]
    except Exception as exc:
        print(f"[DEBUG] LLM call failed: {exc}", flush=True)
        return obs["available_actions"][0]


def run_task(client: OpenAI, task: str, scenario_index: int = 0) -> float:
    max_steps = MAX_STEPS[task]
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task, scenario_index=scenario_index, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_result = env_reset(task, scenario_index)
        obs = reset_result["observation"]

        for step in range(1, max_steps + 1):
            action = get_agent_action(client, obs)
            step_result = env_step(task, action, scenario_index)
            reward = step_result.get("reward", 0.0)
            done = step_result.get("done", False)
            error = step_result["observation"].get("last_action_error")

            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action, reward=reward, done=done, error=error)
            obs = step_result["observation"]

            if done:
                break

        state = env_state(task, scenario_index)
        score = float(state.get("best_grade", max(rewards) if rewards else 0.0))
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Task {task} error: {exc}", flush=True)
        score = 0.0
        success = False

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return score


def run_evaluation(client: OpenAI, scenarios_info: dict, mode: str = "quick") -> Dict[str, Any]:
    """Run evaluation in quick or full mode."""
    results = {"agent_id": AGENT_ID, "model": MODEL_NAME, "mode": mode, "tasks": {}}
    
    for task in TASKS:
        if task not in scenarios_info:
            continue
        
        scenario_count = scenarios_info[task]["count"]
        # In quick mode, test only first scenario. In full mode, test all.
        scenarios_to_test = range(scenario_count) if mode == "full" else [0]
        task_scores = []
        
        if mode == "full":
            print(f"\n{'='*60}")
            print(f"Evaluating {task.upper()} task ({scenario_count} scenarios)")
            print(f"{'='*60}\n")
        
        for scenario_idx in scenarios_to_test:
            score = run_task(client, task, scenario_idx)
            task_scores.append(score)
        
        results["tasks"][task] = {
            "scenarios_tested": len(scenarios_to_test),
            "scores": task_scores,
            "average_score": sum(task_scores) / len(task_scores) if task_scores else 0,
            "success_rate": sum(1 for s in task_scores if s >= SUCCESS_THRESHOLD) / len(task_scores) if task_scores else 0,
        }
    
    return results


def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    print(f"\n{'='*60}")
    print(f"EmailTriageEnv - Evaluation ({EVAL_MODE.upper()} mode)")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Model: {MODEL_NAME}")
    print(f"{'='*60}\n")
    
    # Fetch available scenarios
    scenarios_info = get_scenarios()
    if EVAL_MODE == "full":
        print(f"Available scenarios:")
        for task, info in scenarios_info.items():
            print(f"  - {task}: {info['count']} scenarios")
        print()
    
    # Run evaluation
    results = run_evaluation(client, scenarios_info, mode=EVAL_MODE)
    
    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    for task, task_results in results["tasks"].items():
        print(f"\n{task.upper()}:")
        if EVAL_MODE == "full":
            print(f"  Scenarios: {task_results['scenarios_tested']}")
        print(f"  Avg Score: {task_results['average_score']:.3f}")
        print(f"  Success Rate: {task_results['success_rate']*100:.1f}%")
    
    # Fetch and display agent stats (only in full mode)
    if EVAL_MODE == "full":
        print(f"\n{'='*60}")
        print("AGENT STATISTICS")
        print(f"{'='*60}")
        stats = get_agent_stats()
        if "error" not in stats:
            print(f"Total Episodes: {stats.get('total_episodes', 0)}")
            print(f"Average Score: {stats.get('average_score', 0):.3f}")
            print(f"Success Rate: {stats.get('success_rate', 0)*100:.1f}%")
        
        # Display leaderboard position
        print(f"\n{'='*60}")
        print("LEADERBOARD (Top 10)")
        print(f"{'='*60}")
        leaderboard = get_leaderboard()
        rankings = leaderboard.get("rankings", [])
        for i, entry in enumerate(rankings[:10], 1):
            agent_name = entry.get("agent_id", "unknown")
            score = entry.get("avg_score", 0)
            marker = " ← YOU" if agent_name == AGENT_ID else ""
            print(f"{i:2d}. {agent_name:30s} {score:.3f}{marker}")
    
    print(f"\n{'='*60}")
    print(f"Tip: Set EVAL_MODE=full to test all {sum(info['count'] for info in scenarios_info.values())} scenarios")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
