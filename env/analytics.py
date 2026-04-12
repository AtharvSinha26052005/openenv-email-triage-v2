"""
Analytics and metrics tracking for EmailTriageEnv.
Provides performance insights and leaderboard functionality.
"""
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
import json


class PerformanceTracker:
    """Tracks agent performance metrics across episodes."""
    
    def __init__(self):
        self._episodes: List[Dict[str, Any]] = []
        self._agent_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_episodes": 0,
            "total_score": 0.0,
            "total_steps": 0,
            "successes": 0,
            "failures": 0,
            "task_performance": defaultdict(lambda: {"attempts": 0, "successes": 0, "avg_score": 0.0, "total_score": 0.0}),
        })
        self._session_start = time.time()
    
    def record_episode(
        self,
        agent_id: str,
        task: str,
        scenario_id: str,
        score: float,
        steps: int,
        success: bool,
        duration: float,
        actions: List[str],
        rewards: List[float]
    ):
        """Record a completed episode."""
        episode_data = {
            "agent_id": agent_id,
            "task": task,
            "scenario_id": scenario_id,
            "score": score,
            "steps": steps,
            "success": success,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "actions": actions,
            "rewards": rewards,
        }
        self._episodes.append(episode_data)
        
        # Update agent stats
        stats = self._agent_stats[agent_id]
        stats["total_episodes"] += 1
        stats["total_score"] += score
        stats["total_steps"] += steps
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        
        # Update task-specific performance
        task_perf = stats["task_performance"][task]
        task_perf["attempts"] += 1
        task_perf["total_score"] += score
        task_perf["avg_score"] = task_perf["total_score"] / task_perf["attempts"]
        if success:
            task_perf["successes"] += 1
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for an agent."""
        if agent_id not in self._agent_stats:
            return {"error": "Agent not found"}
        
        stats = self._agent_stats[agent_id]
        total_episodes = stats["total_episodes"]
        
        if total_episodes == 0:
            return {"error": "No episodes recorded"}
        
        return {
            "agent_id": agent_id,
            "total_episodes": total_episodes,
            "average_score": stats["total_score"] / total_episodes,
            "average_steps": stats["total_steps"] / total_episodes,
            "success_rate": stats["successes"] / total_episodes,
            "successes": stats["successes"],
            "failures": stats["failures"],
            "task_breakdown": dict(stats["task_performance"]),
        }
    
    def get_leaderboard(self, task: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard rankings."""
        rankings = []
        
        for agent_id, stats in self._agent_stats.items():
            if task:
                if task not in stats["task_performance"]:
                    continue
                task_perf = stats["task_performance"][task]
                rankings.append({
                    "agent_id": agent_id,
                    "task": task,
                    "attempts": task_perf["attempts"],
                    "avg_score": task_perf["avg_score"],
                    "success_rate": task_perf["successes"] / task_perf["attempts"] if task_perf["attempts"] > 0 else 0,
                })
            else:
                total_episodes = stats["total_episodes"]
                rankings.append({
                    "agent_id": agent_id,
                    "total_episodes": total_episodes,
                    "avg_score": stats["total_score"] / total_episodes if total_episodes > 0 else 0,
                    "success_rate": stats["successes"] / total_episodes if total_episodes > 0 else 0,
                })
        
        # Sort by average score (descending)
        rankings.sort(key=lambda x: x.get("avg_score", 0), reverse=True)
        return rankings[:limit]
    
    def get_recent_episodes(self, limit: int = 20, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent episodes, optionally filtered by agent."""
        episodes = self._episodes
        if agent_id:
            episodes = [ep for ep in episodes if ep["agent_id"] == agent_id]
        return episodes[-limit:]
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across all tasks."""
        task_stats = defaultdict(lambda: {
            "total_attempts": 0,
            "total_successes": 0,
            "total_score": 0.0,
            "avg_score": 0.0,
            "success_rate": 0.0,
        })
        
        for episode in self._episodes:
            task = episode["task"]
            stats = task_stats[task]
            stats["total_attempts"] += 1
            stats["total_score"] += episode["score"]
            if episode["success"]:
                stats["total_successes"] += 1
        
        # Calculate averages
        for task, stats in task_stats.items():
            if stats["total_attempts"] > 0:
                stats["avg_score"] = stats["total_score"] / stats["total_attempts"]
                stats["success_rate"] = stats["total_successes"] / stats["total_attempts"]
        
        return dict(task_stats)
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global environment statistics."""
        total_episodes = len(self._episodes)
        if total_episodes == 0:
            return {"total_episodes": 0, "message": "No episodes recorded"}
        
        total_score = sum(ep["score"] for ep in self._episodes)
        total_successes = sum(1 for ep in self._episodes if ep["success"])
        total_steps = sum(ep["steps"] for ep in self._episodes)
        total_duration = sum(ep["duration"] for ep in self._episodes)
        
        return {
            "total_episodes": total_episodes,
            "unique_agents": len(self._agent_stats),
            "average_score": total_score / total_episodes,
            "success_rate": total_successes / total_episodes,
            "average_steps": total_steps / total_episodes,
            "average_duration": total_duration / total_episodes,
            "uptime_seconds": time.time() - self._session_start,
            "task_statistics": self.get_task_statistics(),
        }
    
    def export_data(self) -> str:
        """Export all tracking data as JSON."""
        return json.dumps({
            "episodes": self._episodes,
            "agent_stats": {k: dict(v) for k, v in self._agent_stats.items()},
            "global_stats": self.get_global_stats(),
        }, indent=2)


# Global tracker instance
_tracker = PerformanceTracker()


def get_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    return _tracker
