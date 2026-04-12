"""
Core OpenEnv environment class for EmailTriageEnv.
"""
import random
from typing import Optional, Dict, Any
from .models import EmailObservation, EmailAction, StepResult, ResetResult
from .dataset import get_scenario
from .graders import grade_action

MAX_STEPS: Dict[str, int] = {"easy": 5, "medium": 5, "hard": 5}


class EmailTriageEnv:
    def __init__(self, task: str = "easy", scenario_index: int = 0):
        if task not in ("easy", "medium", "hard"):
            raise ValueError(f"task must be 'easy', 'medium', or 'hard', got: {task!r}")
        self.task = task
        self.scenario_index = scenario_index
        self._scenario: Optional[Dict[str, Any]] = None
        self._shuffled_actions: list = []
        self._step_count: int = 0
        self._done: bool = False
        self._best_grade: float = 0.0
        self._last_action_result: Optional[str] = None
        self._last_action_error: Optional[str] = None

    def reset(self) -> ResetResult:
        self._scenario = get_scenario(self.task, self.scenario_index)
        # Shuffle available actions to prevent first action from always being correct
        self._shuffled_actions = self._scenario["available_actions"].copy()
        random.shuffle(self._shuffled_actions)
        self._step_count = 0
        self._done = False
        self._best_grade = 0.0
        self._last_action_result = None
        self._last_action_error = None
        obs = self._build_observation()
        return ResetResult(observation=obs, done=False, info={"scenario_id": self._scenario["id"]})

    def step(self, action: EmailAction) -> StepResult:
        if self._scenario is None:
            raise RuntimeError("Call reset() before step()")
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        self._step_count += 1
        max_steps = MAX_STEPS[self.task]
        action_str = action.action.strip()

        # Validate action
        if action_str not in self._shuffled_actions:
            self._last_action_error = f"Invalid action. Must be one of: {self._shuffled_actions}"
            self._last_action_result = None
            done = self._step_count >= max_steps
            self._done = done
            return StepResult(
                observation=self._build_observation(),
                reward=0.05,
                done=done,
                info={"error": self._last_action_error, "grade": 0.0}
            )

        self._last_action_error = None
        grade = grade_action(self.task, action_str, self._scenario)

        if grade > self._best_grade:
            self._best_grade = grade

        if grade >= 0.9:
            self._last_action_result = "Correct! Email(s) triaged successfully."
            self._done = True
        elif grade >= 0.5:
            self._last_action_result = f"Partial credit (score: {grade:.2f}). Some elements correct."
            self._done = True
        else:
            self._last_action_result = "Incorrect. Review the emails and try again."
            self._done = self._step_count >= max_steps

        return StepResult(
            observation=self._build_observation(),
            reward=grade,
            done=self._done,
            info={"grade": grade, "best_grade": self._best_grade, "scenario_id": self._scenario["id"]}
        )

    def state(self) -> Dict[str, Any]:
        if self._scenario is None:
            return {"status": "not_started", "task": self.task}
        return {
            "task": self.task,
            "scenario_id": self._scenario["id"],
            "step": self._step_count,
            "max_steps": MAX_STEPS[self.task],
            "done": self._done,
            "best_grade": self._best_grade,
            "final_score": self._best_grade,
        }

    def _build_observation(self) -> EmailObservation:
        assert self._scenario is not None
        return EmailObservation(
            task=self.task,
            step=self._step_count,
            max_steps=MAX_STEPS[self.task],
            emails=self._scenario["emails"],
            available_actions=self._shuffled_actions,
            context=self._scenario["context"],
            last_action_result=self._last_action_result,
            last_action_error=self._last_action_error,
        )
