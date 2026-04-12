# Quick Start Guide

Get up and running with EmailTriageEnv in 5 minutes!

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip or uv package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎯 Basic Usage

### 1. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:7860`

### 2. Test with Simple Agent

In another terminal:

```bash
python examples/simple_agent.py
```

This runs a rule-based agent across all difficulty levels.

### 3. View Analytics

```bash
python visualize.py
```

See performance charts and leaderboards!

## 🤖 Using an LLM Agent

### Setup

```bash
export HF_TOKEN=your_huggingface_token
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
```

### Run Baseline Agent

```bash
python inference.py
```

### Run Advanced Evaluation

```bash
python inference_advanced.py
```

This tests all 8 scenarios and shows detailed analytics.

## 📊 Checking Your Performance

### Via API

```python
import requests

# Get your stats
response = requests.get("http://localhost:7860/analytics/agent/my_agent")
stats = response.json()

print(f"Episodes: {stats['total_episodes']}")
print(f"Avg Score: {stats['average_score']:.3f}")
print(f"Success Rate: {stats['success_rate']*100:.1f}%")
```

### Via Visualization

```bash
python visualize.py
```

## 🏗️ Building Your Own Agent

### Step 1: Create Agent Function

```python
def my_agent(observation: dict) -> str:
    """
    Your agent logic here.
    
    observation contains:
    - task: "easy" | "medium" | "hard"
    - emails: List of email dicts
    - available_actions: List of valid action strings
    - context: Scenario description
    """
    # Simple example: always pick first action
    return observation["available_actions"][0]
```

### Step 2: Test Your Agent

```python
import requests

SERVER_URL = "http://localhost:7860"
AGENT_ID = "my_custom_agent"

# Reset environment
response = requests.post(
    f"{SERVER_URL}/reset",
    json={"task": "easy", "agent_id": AGENT_ID}
)
obs = response.json()["observation"]

# Get action from your agent
action = my_agent(obs)

# Take step
response = requests.post(
    f"{SERVER_URL}/step",
    json={
        "task": "easy",
        "action": action,
        "agent_id": AGENT_ID
    }
)
result = response.json()

print(f"Reward: {result['reward']}")
print(f"Done: {result['done']}")
```

### Step 3: Batch Evaluate

```python
from env.batch_eval import BatchEvaluator

evaluator = BatchEvaluator()
results = evaluator.evaluate_agent(
    agent_fn=my_agent,
    tasks=["easy", "medium", "hard"]
)

print(f"Overall Score: {results['overall']['average_score']:.3f}")
```

## 🎓 Understanding Tasks

### Easy Task
- **Goal**: Categorize and prioritize a single email
- **Scenarios**: 3 (support issue, billing, newsletter)
- **Actions**: Choose category + priority + action

### Medium Task
- **Goal**: Prioritize multiple emails
- **Scenarios**: 2 (3-4 emails each)
- **Actions**: Determine order and immediate actions

### Hard Task
- **Goal**: Handle complex escalations
- **Scenarios**: 3 (legal threat, data breach, regulatory)
- **Actions**: Choose escalation path and strategy

## 📈 Scoring

- **Perfect**: 0.95 (all criteria correct)
- **Good**: 0.65-0.75 (most criteria correct)
- **Partial**: 0.35-0.55 (some criteria correct)
- **Poor**: 0.05-0.25 (few/no criteria correct)

**Success Threshold**: 0.50

## 🔍 Debugging Tips

### Check Available Scenarios

```bash
curl http://localhost:7860/scenarios
```

### View Specific Scenario

```bash
curl http://localhost:7860/scenarios/easy/0
```

### Monitor Server Health

```bash
curl http://localhost:7860/health
```

### Check Global Stats

```bash
curl http://localhost:7860/analytics/stats
```

## 🐛 Common Issues

### Server Won't Start
- Check if port 7860 is already in use
- Try: `PORT=8000 python app.py`

### Agent Gets Low Scores
- Verify action is in `available_actions`
- Check for typos in action string
- Review scenario context carefully

### Analytics Not Showing
- Ensure you're passing `agent_id` in requests
- Complete at least one full episode
- Check `/analytics/stats` for global data

### LLM Agent Fails
- Verify `HF_TOKEN` is set correctly
- Check API endpoint is accessible
- Try with a different model

## 📚 Next Steps

1. **Read Full Documentation**: Check [README.md](README.md)
2. **Explore Examples**: See [examples/README.md](examples/README.md)
3. **Review API**: Visit `http://localhost:7860/docs`
4. **Join Community**: Open issues/discussions on GitHub

## 🎯 Quick Wins

### Improve Your Agent
1. Parse email subject/body for keywords
2. Check sender domain for importance
3. Look for urgency indicators (URGENT, ASAP)
4. Consider metadata (customer tier, account value)

### Optimize Performance
1. Test on all scenarios, not just one
2. Use batch evaluation for comprehensive testing
3. Analyze failure cases in analytics
4. Compare with other agents on leaderboard

### Contribute
1. Add new email scenarios
2. Improve grading logic
3. Create example agents
4. Enhance documentation

## 💡 Pro Tips

- **Always validate**: Check your action is in `available_actions`
- **Use context**: The `context` field has important hints
- **Test thoroughly**: Run on all scenarios before submitting
- **Monitor analytics**: Track your improvement over time
- **Compare agents**: Use batch evaluation to test variations

## 🏆 Hackathon Tips

1. **Unique Approach**: Try novel decision-making strategies
2. **High Coverage**: Test all 8 scenarios
3. **Good Documentation**: Explain your agent's logic
4. **Performance**: Aim for >80% success rate
5. **Innovation**: Add custom scenarios or grading

## 📞 Get Help

- **Documentation**: [README.md](README.md)
- **Examples**: [examples/](examples/)
- **API Docs**: http://localhost:7860/docs
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Ready to build amazing email triage agents? Let's go! 🚀**
