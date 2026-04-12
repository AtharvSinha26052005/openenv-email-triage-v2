"""
Deterministic graders for all 3 tasks.
Each grader returns a float strictly in (0, 1) — never 0.0 or 1.0.
"""


def grade_easy(action: str, scenario: dict) -> float:
    """Grade single email triage: category + priority + suggested_action."""
    action = action.strip().lower()
    expected_category = scenario["expected_category"].lower()
    expected_priority = scenario["expected_priority"].lower()
    expected_action = scenario["expected_action"].lower()

    score = 0.0
    if expected_category in action:
        score += 0.4
    if expected_priority in action:
        score += 0.3
    if expected_action in action:
        score += 0.3

    return 0.95 if score >= 0.9 else (0.65 if score >= 0.6 else (0.35 if score > 0 else 0.05))


def grade_medium(action: str, scenario: dict) -> float:
    """Grade multi-email triage: prioritized_order + categories + immediate_actions."""
    action = action.strip().lower()
    expected_priority = scenario["expected_priority_first"].lower()
    expected_immediate = scenario["expected_immediate"].lower()

    score = 0.0
    if expected_priority in action:
        score += 0.5
    if expected_immediate in action:
        score += 0.5

    return 0.95 if score >= 0.9 else (0.55 if score >= 0.4 else 0.05)


def grade_hard(action: str, scenario: dict) -> float:
    """Grade complex escalation: category + escalation_path + response_strategy."""
    action = action.strip().lower()
    expected_category = scenario["expected_category"].lower()
    expected_escalation = [e.lower() for e in scenario["expected_escalation"]]

    score = 0.0
    if expected_category in action:
        score += 0.3

    matched = sum(1 for e in expected_escalation if e in action)
    if len(expected_escalation) > 0:
        score += (matched / len(expected_escalation)) * 0.7

    return 0.95 if score >= 0.9 else (0.75 if score >= 0.7 else (0.5 if score >= 0.4 else (0.25 if score > 0 else 0.05)))


def grade_action(task: str, action: str, scenario: dict) -> float:
    """Unified grader dispatcher."""
    if task == "easy":
        return grade_easy(action, scenario)
    elif task == "medium":
        return grade_medium(action, scenario)
    elif task == "hard":
        return grade_hard(action, scenario)
    else:
        raise ValueError(f"Unknown task: {task}")
