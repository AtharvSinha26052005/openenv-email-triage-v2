# EmailTriageEnv Examples

This directory contains example agents and usage patterns for the EmailTriageEnv.

## Examples

### 1. Simple Rule-Based Agent (`simple_agent.py`)

A basic agent that uses keyword matching and simple heuristics to make triage decisions.

**Run it:**
```bash
# Start the server first
python app.py

# In another terminal
python examples/simple_agent.py
```

**What it demonstrates:**
- Basic environment interaction (reset, step, state)
- Rule-based decision making without LLM
- Analytics integration
- Error handling

### 2. LLM-Powered Agent (`../inference.py`)

The baseline agent using OpenAI-compatible LLM APIs.

**Run it:**
```bash
export HF_TOKEN=your_token
python inference.py
```

### 3. Advanced Evaluation (`../inference_advanced.py`)

Comprehensive evaluation across all scenarios with detailed analytics.

**Run it:**
```bash
export HF_TOKEN=your_token
export AGENT_ID=my_custom_agent
python inference_advanced.py
```

## Creating Your Own Agent

### Basic Template

```python
import requests

SERVER_URL = "http://localhost:7860"
AGENT_ID = "my_agent"

def my_agent_function(observation: dict) -> str:
    """
    Your agent logic here.
    
    Args:
        observation: Dict containing:
            - task: str (easy/medium/hard)
            - step: int
            - max_steps: int
            - emails: List[dict]
            - available_actions: List[str]
            - context: str
    
    Returns:
        action: str (must be one of available_actions)
    """
    # Your decision logic
    return observation["available_actions"][0]

# Reset environment
response = requests.post(
    f"{SERVER_URL}/reset",
    json={"task": "easy", "agent_id": AGENT_ID}
)
obs = response.json()["observation"]

# Take action
action = my_agent_function(obs)
response = requests.post(
    f"{SERVER_URL}/step",
    json={"task": "easy", "action": action, "agent_id": AGENT_ID}
)
result = response.json()
```

### Using the Batch Evaluator

```python
from env.batch_eval import BatchEvaluator

def my_agent(obs: dict) -> str:
    # Your logic
    return obs["available_actions"][0]

evaluator = BatchEvaluator()
results = evaluator.evaluate_agent(
    agent_fn=my_agent,
    tasks=["easy", "medium", "hard"]
)

print(f"Overall score: {results['overall']['average_score']:.3f}")
```

### Comparing Multiple Agents

```python
from env.batch_eval import compare_agents

def agent_a(obs): return obs["available_actions"][0]
def agent_b(obs): return obs["available_actions"][-1]

results = compare_agents({
    "Agent A": agent_a,
    "Agent B": agent_b
})

print("Rankings:", results["rankings"]["by_overall_score"])
```

## Tips for Building Better Agents

### 1. Analyze Email Content
- Look for urgency indicators (URGENT, ASAP, deadline)
- Identify sender importance (VIP, executive, regulatory)
- Detect risk factors (legal, security, financial)

### 2. Use Context
- The `context` field provides important scenario information
- Consider business impact and compliance requirements

### 3. Handle Edge Cases
- Always validate your action is in `available_actions`
- Implement fallback logic for unexpected scenarios
- Handle API errors gracefully

### 4. Optimize for Metrics
- Aim for high scores (>0.9 for perfect)
- Minimize steps to completion
- Maximize success rate across all tasks

### 5. Test Thoroughly
- Test on all difficulty levels
- Try multiple scenarios per task
- Use batch evaluation for comprehensive testing

## Analytics Integration

All agents automatically get tracked in the analytics system:

```python
# View your agent's stats
response = requests.get(f"{SERVER_URL}/analytics/agent/{AGENT_ID}")
stats = response.json()

# Check leaderboard position
response = requests.get(f"{SERVER_URL}/analytics/leaderboard")
leaderboard = response.json()

# Export all data
response = requests.get(f"{SERVER_URL}/analytics/export")
data = response.json()
```

## Visualization

Generate performance reports:

```bash
python visualize.py http://localhost:7860
```

This creates ASCII charts showing:
- Global statistics
- Task performance breakdown
- Leaderboard rankings
- Success rate comparisons

## Advanced Features

### Custom Scenarios

Add your own scenarios in `env/dataset.py`:

```python
SCENARIOS["easy"].append({
    "id": "easy_custom",
    "emails": [...],
    "context": "...",
    "available_actions": [...],
    "expected_category": "...",
    "expected_priority": "...",
    "expected_action": "..."
})
```

### Custom Grading

Modify grading logic in `env/graders.py` to change how actions are scored.

### Parallel Evaluation

Use parallel evaluation for faster testing:

```python
from env.batch_eval import BatchEvaluator

evaluator = BatchEvaluator(max_workers=8)
results = evaluator.parallel_evaluate(my_agent)
```

## Need Help?

- Check the main README.md for full documentation
- Review the API reference at `/docs` endpoint
- Open an issue on GitHub
