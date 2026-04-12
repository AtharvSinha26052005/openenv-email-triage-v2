"""
Batch evaluation utilities for testing agents across multiple scenarios.
"""
from typing import List, Dict, Any, Callable, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .environment import EmailTriageEnv
from .models import EmailAction
from .dataset import SCENARIOS


class BatchEvaluator:
    """Evaluate agents across multiple scenarios in parallel."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def evaluate_agent(
        self,
        agent_fn: Callable[[Dict[str, Any]], str],
        tasks: Optional[List[str]] = None,
        scenario_indices: Optional[Dict[str, List[int]]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate an agent across multiple tasks and scenarios.
        
        Args:
            agent_fn: Function that takes observation dict and returns action string
            tasks: List of tasks to evaluate (default: all tasks)
            scenario_indices: Dict mapping task names to scenario indices to test
        
        Returns:
            Comprehensive evaluation results
        """
        if tasks is None:
            tasks = ["easy", "medium", "hard"]
        
        if scenario_indices is None:
            scenario_indices = {
                task: list(range(len(SCENARIOS[task])))
                for task in tasks
            }
        
        results = {
            "tasks": {},
            "overall": {
                "total_episodes": 0,
                "total_score": 0.0,
                "total_successes": 0,
                "total_steps": 0,
                "total_duration": 0.0,
            }
        }
        
        # Evaluate each task
        for task in tasks:
            task_results = self._evaluate_task(
                agent_fn,
                task,
                scenario_indices.get(task, [0])
            )
            results["tasks"][task] = task_results
            
            # Update overall stats
            results["overall"]["total_episodes"] += task_results["episodes"]
            results["overall"]["total_score"] += task_results["total_score"]
            results["overall"]["total_successes"] += task_results["successes"]
            results["overall"]["total_steps"] += task_results["total_steps"]
            results["overall"]["total_duration"] += task_results["total_duration"]
        
        # Calculate overall averages
        total_eps = results["overall"]["total_episodes"]
        if total_eps > 0:
            results["overall"]["average_score"] = results["overall"]["total_score"] / total_eps
            results["overall"]["success_rate"] = results["overall"]["total_successes"] / total_eps
            results["overall"]["average_steps"] = results["overall"]["total_steps"] / total_eps
            results["overall"]["average_duration"] = results["overall"]["total_duration"] / total_eps
        
        return results
    
    def _evaluate_task(
        self,
        agent_fn: Callable[[Dict[str, Any]], str],
        task: str,
        scenario_indices: List[int]
    ) -> Dict[str, Any]:
        """Evaluate agent on a specific task across multiple scenarios."""
        episodes = []
        
        for scenario_idx in scenario_indices:
            episode_result = self._run_episode(agent_fn, task, scenario_idx)
            episodes.append(episode_result)
        
        # Aggregate results
        total_score = sum(ep["score"] for ep in episodes)
        successes = sum(1 for ep in episodes if ep["success"])
        total_steps = sum(ep["steps"] for ep in episodes)
        total_duration = sum(ep["duration"] for ep in episodes)
        
        return {
            "task": task,
            "episodes": len(episodes),
            "scenarios_tested": scenario_indices,
            "total_score": total_score,
            "average_score": total_score / len(episodes) if episodes else 0,
            "successes": successes,
            "success_rate": successes / len(episodes) if episodes else 0,
            "total_steps": total_steps,
            "average_steps": total_steps / len(episodes) if episodes else 0,
            "total_duration": total_duration,
            "episode_details": episodes,
        }
    
    def _run_episode(
        self,
        agent_fn: Callable[[Dict[str, Any]], str],
        task: str,
        scenario_index: int
    ) -> Dict[str, Any]:
        """Run a single episode."""
        env = EmailTriageEnv(task=task, scenario_index=scenario_index)
        start_time = time.time()
        
        reset_result = env.reset()
        obs = reset_result.observation.model_dump()
        
        steps = 0
        rewards = []
        actions_taken = []
        done = False
        
        while not done and steps < 5:
            # Get action from agent
            try:
                action_str = agent_fn(obs)
                actions_taken.append(action_str)
            except Exception as e:
                action_str = obs["available_actions"][0]  # Fallback
                actions_taken.append(f"ERROR:{str(e)}")
            
            # Take step
            action = EmailAction(action=action_str)
            step_result = env.step(action)
            
            rewards.append(step_result.reward)
            done = step_result.done
            obs = step_result.observation.model_dump()
            steps += 1
        
        duration = time.time() - start_time
        final_state = env.state()
        
        return {
            "task": task,
            "scenario_id": final_state["scenario_id"],
            "scenario_index": scenario_index,
            "score": final_state["best_grade"],
            "success": final_state["best_grade"] >= 0.5,
            "steps": steps,
            "duration": duration,
            "rewards": rewards,
            "actions": actions_taken,
        }
    
    def parallel_evaluate(
        self,
        agent_fn: Callable[[Dict[str, Any]], str],
        tasks: Optional[List[str]] = None,
        scenario_indices: Optional[Dict[str, List[int]]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate agent in parallel across multiple scenarios.
        Faster for large-scale evaluations.
        """
        if tasks is None:
            tasks = ["easy", "medium", "hard"]
        
        if scenario_indices is None:
            scenario_indices = {
                task: list(range(len(SCENARIOS[task])))
                for task in tasks
            }
        
        # Create all evaluation tasks
        eval_tasks = []
        for task in tasks:
            for scenario_idx in scenario_indices.get(task, [0]):
                eval_tasks.append((task, scenario_idx))
        
        # Run evaluations in parallel
        episodes = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_episode, agent_fn, task, idx): (task, idx)
                for task, idx in eval_tasks
            }
            
            for future in as_completed(futures):
                try:
                    episode_result = future.result()
                    episodes.append(episode_result)
                except Exception as e:
                    task, idx = futures[future]
                    episodes.append({
                        "task": task,
                        "scenario_index": idx,
                        "error": str(e),
                        "score": 0.0,
                        "success": False,
                    })
        
        # Aggregate results by task
        results = {"tasks": {}, "overall": {}}
        
        for task in tasks:
            task_episodes = [ep for ep in episodes if ep["task"] == task]
            if task_episodes:
                total_score = sum(ep["score"] for ep in task_episodes)
                successes = sum(1 for ep in task_episodes if ep["success"])
                
                results["tasks"][task] = {
                    "episodes": len(task_episodes),
                    "average_score": total_score / len(task_episodes),
                    "success_rate": successes / len(task_episodes),
                    "episode_details": task_episodes,
                }
        
        # Overall stats
        if episodes:
            total_score = sum(ep["score"] for ep in episodes)
            successes = sum(1 for ep in episodes if ep["success"])
            
            results["overall"] = {
                "total_episodes": len(episodes),
                "average_score": total_score / len(episodes),
                "success_rate": successes / len(episodes),
            }
        
        return results


def compare_agents(
    agents: Dict[str, Callable[[Dict[str, Any]], str]],
    tasks: Optional[List[str]] = None,
    scenario_indices: Optional[Dict[str, List[int]]] = None,
) -> Dict[str, Any]:
    """
    Compare multiple agents side-by-side.
    
    Args:
        agents: Dict mapping agent names to agent functions
        tasks: List of tasks to evaluate
        scenario_indices: Scenarios to test
    
    Returns:
        Comparison results with rankings
    """
    evaluator = BatchEvaluator()
    results = {}
    
    for agent_name, agent_fn in agents.items():
        print(f"Evaluating {agent_name}...")
        results[agent_name] = evaluator.evaluate_agent(agent_fn, tasks, scenario_indices)
    
    # Create comparison table
    comparison = {
        "agents": {},
        "rankings": {
            "by_overall_score": [],
            "by_success_rate": [],
            "by_task": {},
        }
    }
    
    for agent_name, agent_results in results.items():
        comparison["agents"][agent_name] = agent_results["overall"]
    
    # Rank by overall score
    comparison["rankings"]["by_overall_score"] = sorted(
        [(name, res["overall"].get("average_score", 0)) for name, res in results.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by success rate
    comparison["rankings"]["by_success_rate"] = sorted(
        [(name, res["overall"].get("success_rate", 0)) for name, res in results.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by task
    if tasks:
        for task in tasks:
            task_rankings = []
            for agent_name, agent_results in results.items():
                if task in agent_results["tasks"]:
                    score = agent_results["tasks"][task].get("average_score", 0)
                    task_rankings.append((agent_name, score))
            
            comparison["rankings"]["by_task"][task] = sorted(
                task_rankings,
                key=lambda x: x[1],
                reverse=True
            )
    
    return comparison
