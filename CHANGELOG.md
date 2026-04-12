# Changelog

All notable changes to EmailTriageEnv will be documented in this file.

## [2.0.0] - 2024-01-18

### 🎉 Major Release - Hackathon Edition

This release transforms EmailTriageEnv from a basic environment into a production-ready, feature-rich platform for training and evaluating email triage agents.

### Added

#### 📊 Analytics System
- **Performance Tracking**: Automatic recording of all agent interactions
  - Episode-level metrics (score, steps, duration, actions, rewards)
  - Agent-specific statistics aggregation
  - Task-specific performance breakdown
- **Leaderboard System**: Global and task-specific rankings
  - Real-time updates
  - Success rate tracking
  - Average score calculations
- **Data Export**: JSON export of complete analytics data
- **New Endpoints**:
  - `GET /analytics/stats` - Global statistics
  - `GET /analytics/agent/{agent_id}` - Agent-specific stats
  - `GET /analytics/leaderboard` - Rankings (with task filter)
  - `GET /analytics/recent` - Recent episodes
  - `GET /analytics/export` - Data export

#### 🎯 Expanded Scenarios
- **Easy Task**: 3 scenarios (was 1)
  - Account access issue
  - Billing verification
  - Newsletter/low-priority
- **Medium Task**: 2 scenarios (was 1)
  - Payment overdue + partnership + newsletter
  - Security alert + HR reminder + CEO meeting + sales offer
- **Hard Task**: 3 scenarios (was 1)
  - VIP customer legal threat
  - Media inquiry about data breach
  - Government regulatory investigation
- **Total**: 8 diverse scenarios testing different aspects

#### 🚀 Batch Evaluation
- `BatchEvaluator` class for automated testing
- Parallel evaluation support with configurable workers
- Agent comparison functionality
- Comprehensive result aggregation
- Statistical analysis tools

#### 📈 Visualization Tools
- `visualize.py` - Analytics visualization script
- ASCII bar charts for performance metrics
- Task performance breakdown
- Leaderboard display
- Global statistics overview

#### 🔧 Enhanced Tools
- `inference_advanced.py` - Comprehensive evaluation script
  - Tests all scenarios automatically
  - Displays agent statistics
  - Shows leaderboard position
  - Detailed progress logging
- `examples/simple_agent.py` - Rule-based agent example
- `examples/README.md` - Comprehensive examples documentation

#### 🌐 API Improvements
- **CORS Support**: Web-based agents now supported
- **Agent Tracking**: `agent_id` parameter for all endpoints
- **Episode Tracking**: Automatic session management
- **Scenario Discovery**:
  - `GET /scenarios` - List all scenarios
  - `GET /scenarios/{task}/{index}` - Scenario details
- **Enhanced Responses**: Episode keys and tracking info

### Changed

#### 🔄 Breaking Changes
- API version bumped to 2.0.0
- Request models now include optional `agent_id` field
- `/reset` endpoint returns `episode_key` for tracking
- `/step` endpoint automatically records to analytics when episode completes

#### 📝 Documentation
- Completely rewritten README with comprehensive documentation
- Added Analytics & Leaderboard section
- Added Batch Evaluation section
- Expanded API Reference
- Updated project structure
- Added examples directory with guides

#### ⚡ Performance
- Optimized environment instance management
- Efficient episode tracking with automatic cleanup
- Parallel evaluation support for faster testing

### Fixed
- Division by zero in graders when expected_escalation is empty
- Improved error handling in analytics endpoints
- Better validation for scenario indices

### Technical Details

#### New Dependencies
- No new external dependencies required
- All features use existing FastAPI, Pydantic stack

#### Architecture Improvements
- Modular analytics system (`env/analytics.py`)
- Separate batch evaluation module (`env/batch_eval.py`)
- Clean separation of concerns
- Backward compatible with v1.0 agents

#### Testing
- 8 scenarios across 3 difficulty levels
- Comprehensive test coverage
- Example agents for validation

---

## [1.0.0] - 2024-01-15

### Initial Release

#### Features
- OpenEnv-compliant RL environment
- 3 difficulty levels (easy, medium, hard)
- 3 scenarios (1 per difficulty)
- Deterministic grading system
- FastAPI server with REST API
- Docker deployment support
- Baseline LLM agent
- MCP protocol support

#### Endpoints
- `POST /reset` - Initialize episode
- `POST /step` - Take action
- `POST /state` - Get state
- `GET /tasks` - List tasks
- `GET /metadata` - Environment info
- `GET /schema` - API schemas
- `GET /health` - Health check
- `POST /mcp` - MCP protocol

---

## Upgrade Guide

### From v1.0 to v2.0

#### For Agent Developers

**Optional**: Add `agent_id` to your requests for analytics tracking:

```python
# Before (still works)
requests.post("/reset", json={"task": "easy"})

# After (recommended)
requests.post("/reset", json={"task": "easy", "agent_id": "my_agent"})
```

**New**: Access analytics for your agent:

```python
stats = requests.get(f"/analytics/agent/{agent_id}").json()
print(f"Success rate: {stats['success_rate']}")
```

#### For Environment Users

**New Scenarios**: Update your evaluation loops to test all scenarios:

```python
# Before
for task in ["easy", "medium", "hard"]:
    run_episode(task, scenario_index=0)

# After
scenarios = requests.get("/scenarios").json()
for task, info in scenarios.items():
    for idx in range(info["count"]):
        run_episode(task, scenario_index=idx)
```

**Batch Evaluation**: Use the new batch evaluator:

```python
from env.batch_eval import BatchEvaluator

evaluator = BatchEvaluator()
results = evaluator.evaluate_agent(my_agent_fn)
```

#### Backward Compatibility

All v1.0 code continues to work without modifications. New features are opt-in through:
- Optional `agent_id` parameters
- New analytics endpoints
- Additional scenarios (accessed via `scenario_index`)

---

## Future Roadmap

### v2.1 (Planned)
- [ ] Web UI for environment interaction
- [ ] Real-time leaderboard updates via WebSocket
- [ ] Agent replay functionality
- [ ] Performance profiling tools

### v2.2 (Planned)
- [ ] Multi-language email support
- [ ] Custom scenario builder API
- [ ] Advanced grading with LLM judges
- [ ] Integration with popular RL frameworks

### v3.0 (Future)
- [ ] Dynamic difficulty adjustment
- [ ] Temporal email sequences
- [ ] Multi-agent collaboration scenarios
- [ ] Production deployment templates

---

## Contributing

We welcome contributions! Areas of interest:
- New email scenarios
- Additional grading strategies
- Performance optimizations
- Documentation improvements
- Example agents

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
