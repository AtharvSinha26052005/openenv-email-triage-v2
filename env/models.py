from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EmailObservation(BaseModel):
    task: str = Field(..., description="Task name: easy | medium | hard")
    step: int
    max_steps: int
    emails: List[Dict[str, Any]]
    available_actions: List[str]
    context: str
    last_action_result: Optional[str] = None
    last_action_error: Optional[str] = None


class EmailAction(BaseModel):
    action: str = Field(..., description="One of the available_actions strings")


class StepResult(BaseModel):
    observation: EmailObservation
    reward: float = Field(..., ge=0.0, le=1.0)
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class ResetResult(BaseModel):
    observation: EmailObservation
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)
