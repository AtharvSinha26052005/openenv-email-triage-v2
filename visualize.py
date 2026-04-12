"""
Visualization utilities for EmailTriageEnv analytics.
Generates performance charts and comparison graphs.
"""
import json
import urllib.request
from typing import Dict, Any, List, Optional


def fetch_analytics(server_url: str = "http://localhost:7860") -> Dict[str, Any]:
    """Fetch analytics data from server."""
    req = urllib.request.Request(f"{server_url}/analytics/stats", method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_leaderboard(server_url: str = "http://localhost:7860", task: Optional[str] = None) -> Dict[str, Any]:
    """Fetch leaderboard data from server."""
    path = f"{server_url}/analytics/leaderboard"
    if task:
        path += f"?task={task}"
    req = urllib.request.Request(path, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def print_ascii_bar_chart(data: List[tuple], title: str, max_width: int = 50):
    """Print an ASCII bar chart."""
    print(f"\n{title}")
    print("=" * (max_width + 30))
    
    if not data:
        print("No data available")
        return
    
    max_value = max(value for _, value in data)
    if max_value == 0:
        max_value = 1
    
    for label, value in data:
        bar_length = int((value / max_value) * max_width)
        bar = "█" * bar_length
        print(f"{label:20s} {bar} {value:.3f}")
    
    print()


def print_task_performance(stats: Dict[str, Any]):
    """Print task performance breakdown."""
    task_stats = stats.get("task_statistics", {})
    
    if not task_stats:
        print("No task statistics available")
        return
    
    print("\n" + "="*60)
    print("TASK PERFORMANCE BREAKDOWN")
    print("="*60)
    
    for task, data in task_stats.items():
        print(f"\n{task.upper()}:")
        print(f"  Attempts:     {data.get('total_attempts', 0)}")
        print(f"  Successes:    {data.get('total_successes', 0)}")
        print(f"  Avg Score:    {data.get('avg_score', 0):.3f}")
        print(f"  Success Rate: {data.get('success_rate', 0)*100:.1f}%")
    
    # Create bar chart for average scores
    score_data = [(task.upper(), data.get('avg_score', 0)) for task, data in task_stats.items()]
    print_ascii_bar_chart(score_data, "\nAverage Scores by Task", max_width=40)
    
    # Create bar chart for success rates
    success_data = [(task.upper(), data.get('success_rate', 0)) for task, data in task_stats.items()]
    print_ascii_bar_chart(success_data, "Success Rates by Task", max_width=40)


def print_leaderboard_chart(leaderboard: Dict[str, Any], limit: int = 10):
    """Print leaderboard as a chart."""
    rankings = leaderboard.get("rankings", [])[:limit]
    
    if not rankings:
        print("No leaderboard data available")
        return
    
    print("\n" + "="*60)
    print(f"TOP {limit} AGENTS - LEADERBOARD")
    print("="*60)
    
    chart_data = []
    for i, entry in enumerate(rankings, 1):
        agent_id = entry.get("agent_id", "unknown")
        score = entry.get("avg_score", 0)
        success_rate = entry.get("success_rate", 0)
        
        # Truncate long agent names
        if len(agent_id) > 25:
            agent_id = agent_id[:22] + "..."
        
        label = f"{i:2d}. {agent_id}"
        chart_data.append((label, score))
        
        print(f"{i:2d}. {agent_id:30s} Score: {score:.3f} | Success: {success_rate*100:.1f}%")
    
    print_ascii_bar_chart(chart_data, "\nScore Distribution", max_width=40)


def print_global_overview(stats: Dict[str, Any]):
    """Print global statistics overview."""
    print("\n" + "="*60)
    print("GLOBAL ENVIRONMENT STATISTICS")
    print("="*60)
    
    print(f"\nTotal Episodes:    {stats.get('total_episodes', 0)}")
    print(f"Unique Agents:     {stats.get('unique_agents', 0)}")
    print(f"Average Score:     {stats.get('average_score', 0):.3f}")
    print(f"Success Rate:      {stats.get('success_rate', 0)*100:.1f}%")
    print(f"Avg Steps/Episode: {stats.get('average_steps', 0):.1f}")
    print(f"Avg Duration:      {stats.get('average_duration', 0):.2f}s")
    
    uptime = stats.get('uptime_seconds', 0)
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    print(f"Uptime:            {hours}h {minutes}m")


def generate_report(server_url: str = "http://localhost:7860"):
    """Generate a comprehensive analytics report."""
    try:
        print("\n" + "="*60)
        print("EMAIL TRIAGE ENVIRONMENT - ANALYTICS REPORT")
        print("="*60)
        
        # Fetch and display global stats
        stats = fetch_analytics(server_url)
        print_global_overview(stats)
        
        # Display task performance
        print_task_performance(stats)
        
        # Display leaderboard
        leaderboard = fetch_leaderboard(server_url)
        print_leaderboard_chart(leaderboard, limit=10)
        
        # Task-specific leaderboards
        for task in ["easy", "medium", "hard"]:
            try:
                task_leaderboard = fetch_leaderboard(server_url, task=task)
                print(f"\n" + "="*60)
                print(f"TOP 5 AGENTS - {task.upper()} TASK")
                print("="*60)
                
                rankings = task_leaderboard.get("rankings", [])[:5]
                for i, entry in enumerate(rankings, 1):
                    agent_id = entry.get("agent_id", "unknown")
                    score = entry.get("avg_score", 0)
                    attempts = entry.get("attempts", 0)
                    print(f"{i}. {agent_id:30s} Score: {score:.3f} ({attempts} attempts)")
            except Exception as e:
                print(f"Could not fetch {task} leaderboard: {e}")
        
        print("\n" + "="*60)
        print("Report generated successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        print("Make sure the server is running at", server_url)


def main():
    import sys
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7860"
    generate_report(server_url)


if __name__ == "__main__":
    main()
