---
title: EmailTriageEnv v2.0
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 📧 EmailTriageEnv - OpenEnv Meta Hackathon

**An OpenEnv-compliant Reinforcement Learning environment for training AI agents to intelligently triage and prioritize emails**

🔗 [GitHub Repository](https://github.com/AtharvSinha26052005/openenv-email-triage-v2) | 📚 [Full Documentation](https://github.com/AtharvSinha26052005/openenv-email-triage-v2#readme)

---

##  What is EmailTriageEnv?

EmailTriageEnv is a production-ready RL environment that simulates real-world email management challenges. Built for the **OpenEnv Meta Hackathon**, it enables AI agents to learn sophisticated email triage strategies through structured interaction and reward-based learning.

### Key Features

- ✅ **OpenEnv Compliant**: Fully standardized API following OpenEnv specification
- 🎯 **8 Diverse Scenarios**: Progressive difficulty from easy to hard
- 📊 **Analytics System**: Automatic performance tracking and leaderboards
- 🚀 **Batch Evaluation**: Test agents across all scenarios
- 📈 **Visualization Tools**: ASCII charts and performance reports
- 🔧 **RESTful API**: Easy integration with any agent framework

---

## 🚀 Quick Start

### API Endpoints

The environment is running at: `https://atharv9-openenv-email-triage-v2.hf.space`

**Core Endpoints:**
- `POST /reset` - Initialize a new episode
- `POST /step` - Execute an action
- `POST /state` - Get current state
- `GET /tasks` - List available tasks
- `GET /scenarios` - List all scenarios
- `GET /health` - Health check

**Analytics Endpoints:**
- `GET /analytics/stats` - Global statistics
- `GET /analytics/leaderboard` - Rankings
- `GET /analytics/agent/{agent_id}` - Agent-specific stats

### Example Usage

```python
import requests

# Reset environment
response = requests.post(
    "https://atharv9-openenv-email-triage-v2.hf.space/reset",
    json={"task": "easy", "scenario_index": 0}
)
obs = response.json()["observation"]

# Take action
action = obs["available_actions"][0]
response = requests.post(
    "https://atharv9-openenv-email-triage-v2.hf.space/step",
    json={"task": "easy", "action": action}
)
result = response.json()
print(f"Reward: {result['reward']}")
```

---

## 📚 Task Types

### 🟢 Easy: Single Email Triage
Categorize, prioritize, and suggest action for a single email.
- **Scenarios**: 3
- **Max Steps**: 5
- **Scoring**: Category (40%) + Priority (30%) + Action (30%)

### 🟡 Medium: Multi-Email Prioritization
Triage multiple emails and determine handling order.
- **Scenarios**: 2
- **Max Steps**: 5
- **Scoring**: Priority order (50%) + Immediate action (50%)

### 🔴 Hard: Complex Escalation
Handle sensitive VIP complaints with legal and business risks.
- **Scenarios**: 3
- **Max Steps**: 5
- **Scoring**: Category (30%) + Escalation path (70%)

---

## 🎉 What's New in v2.0

- 📊 Analytics system with leaderboards
- 🎯 Expanded from 3 to 8 scenarios
- 🚀 Batch evaluation support
- 📈 Visualization tools
- 🔧 10+ new API endpoints
- 🌐 CORS support for web agents
- 🐛 Fixed scoring system (now dynamic 0.05-0.95)

---

## 📖 Documentation

For complete documentation, examples, and guides, visit:
👉 [GitHub Repository](https://github.com/AtharvSinha26052005/openenv-email-triage-v2)

---

## 🏆 OpenEnv Meta Hackathon

This project was built for the OpenEnv Meta Hackathon, demonstrating:
- Real-world application of RL environments
- Production-quality code and architecture
- Comprehensive testing and evaluation tools
- Full OpenEnv specification compliance

---

## 👥 Team

Built with ❤️ by Atharv Sinha

- **GitHub**: [@AtharvSinha26052005](https://github.com/AtharvSinha26052005)
- **Hugging Face**: [@atharv9](https://huggingface.co/atharv9)

---

## 📜 License

MIT License - See [LICENSE](https://github.com/AtharvSinha26052005/openenv-email-triage-v2/blob/main/LICENSE) for details.
