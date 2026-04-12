"""
Simple rule-based agent example for EmailTriageEnv.
Demonstrates basic interaction without LLM.
"""
import requests
import time

SERVER_URL = "http://localhost:7860"
AGENT_ID = "simple_rule_based_agent"


def simple_agent(observation: dict) -> str:
    """
    Simple rule-based agent that makes decisions based on keywords.
    """
    emails = observation["emails"]
    available_actions = observation["available_actions"]
    task = observation["task"]
    
    if task == "easy":
        # Single email - check for urgency keywords
        email = emails[0]
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        
        # Check for urgent/critical keywords
        if any(word in subject + body for word in ["urgent", "cannot", "error", "help", "issue"]):
            # Look for high priority support action
            for action in available_actions:
                if "priority:high" in action and "support" in action:
                    return action
        
        # Check for billing keywords
        if any(word in subject + body for word in ["payment", "invoice", "billing", "charge"]):
            for action in available_actions:
                if "billing" in action:
                    return action
        
        # Default to first action
        return available_actions[0]
    
    elif task == "medium":
        # Multiple emails - look for urgent ones
        for email in emails:
            subject = email.get("subject", "").lower()
            if "urgent" in subject or "overdue" in subject:
                email_id = email.get("id", "")
                # Find action that prioritizes this email
                for action in available_actions:
                    if email_id in action and "immediate" in action:
                        return action
        
        return available_actions[0]
    
    elif task == "hard":
        # Complex escalation - look for critical keywords
        email = emails[0]
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        
        # Check for legal/crisis keywords
        if any(word in subject + body for word in ["legal", "lawsuit", "breach", "regulator"]):
            for action in available_actions:
                if "critical" in action or "crisis" in action or "legal" in action:
                    return action
        
        return available_actions[0]
    
    return available_actions[0]


def run_episode(task: str, scenario_index: int = 0):
    """Run a single episode with the simple agent."""
    print(f"\n{'='*50}")
    print(f"Running {task} task (scenario {scenario_index})")
    print(f"{'='*50}")
    
    # Reset environment
    response = requests.post(
        f"{SERVER_URL}/reset",
        json={"task": task, "scenario_index": scenario_index, "agent_id": AGENT_ID}
    )
    
    if response.status_code != 200:
        print(f"Error resetting: {response.text}")
        return
    
    result = response.json()
    observation = result["observation"]
    
    # Print email info
    print(f"\nEmails received: {len(observation['emails'])}")
    for i, email in enumerate(observation['emails'], 1):
        print(f"  {i}. From: {email.get('from', 'unknown')}")
        print(f"     Subject: {email.get('subject', 'no subject')}")
    
    step = 0
    done = False
    
    while not done and step < 5:
        step += 1
        
        # Get action from agent
        action = simple_agent(observation)
        print(f"\nStep {step}: Taking action")
        print(f"  Action: {action[:80]}...")
        
        # Take step
        response = requests.post(
            f"{SERVER_URL}/step",
            json={
                "task": task,
                "action": action,
                "scenario_index": scenario_index,
                "agent_id": AGENT_ID
            }
        )
        
        if response.status_code != 200:
            print(f"Error stepping: {response.text}")
            break
        
        result = response.json()
        reward = result["reward"]
        done = result["done"]
        observation = result["observation"]
        
        print(f"  Reward: {reward:.2f}")
        print(f"  Done: {done}")
        
        if observation.get("last_action_result"):
            print(f"  Result: {observation['last_action_result']}")
        if observation.get("last_action_error"):
            print(f"  Error: {observation['last_action_error']}")
    
    # Get final state
    response = requests.post(
        f"{SERVER_URL}/state",
        json={"task": task, "scenario_index": scenario_index}
    )
    
    if response.status_code == 200:
        state = response.json()
        print(f"\nFinal Score: {state.get('best_grade', 0):.3f}")
        print(f"Success: {state.get('best_grade', 0) >= 0.5}")


def main():
    print("="*50)
    print("Simple Rule-Based Agent Demo")
    print("="*50)
    
    # Test on all difficulty levels
    for task in ["easy", "medium", "hard"]:
        run_episode(task, scenario_index=0)
        time.sleep(0.5)
    
    # Fetch agent stats
    print(f"\n{'='*50}")
    print("Agent Statistics")
    print(f"{'='*50}")
    
    try:
        response = requests.get(f"{SERVER_URL}/analytics/agent/{AGENT_ID}")
        if response.status_code == 200:
            stats = response.json()
            print(f"\nTotal Episodes: {stats.get('total_episodes', 0)}")
            print(f"Average Score: {stats.get('average_score', 0):.3f}")
            print(f"Success Rate: {stats.get('success_rate', 0)*100:.1f}%")
        else:
            print("No stats available yet")
    except Exception as e:
        print(f"Could not fetch stats: {e}")


if __name__ == "__main__":
    main()
