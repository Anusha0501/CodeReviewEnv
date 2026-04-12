"""Pydantic models for CodeReviewEnv"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class BugType(str, Enum):
    """Types of bugs that can be detected"""
    SYNTAX = "syntax"
    LOGIC = "logic"
    SECURITY = "security"
    PERFORMANCE = "performance"


class Observation(BaseModel):
    """Environment observation representing code review context"""
    code_diff: str = Field(..., description="Git-style diff of the code changes")
    file_name: str = Field(..., description="Name of the file being reviewed")
    language: str = Field(..., description="Programming language")
    context: str = Field(..., description="Additional context about the code")
    previous_comments: List[str] = Field(default_factory=list, description="Previous reviewer comments")
    step_count: int = Field(default=0, description="Current step number")
    
    class Config:
        json_encoders = {
            BugType: lambda v: v.value
        }


class Action(BaseModel):
    """Agent action for code review"""
    reviewer_comment: str = Field(..., description="Comment about the code")
    bug_detected: bool = Field(..., description="Whether a bug was detected")
    bug_type: Optional[BugType] = Field(None, description="Type of bug detected")
    
    class Config:
        json_encoders = {
            BugType: lambda v: v.value
        }


class Reward(BaseModel):
    """Reward signal for the agent"""
    score: float = Field(..., description="Total reward score (0.0 to 1.0)")
    detection_reward: float = Field(default=0.0, description="Reward for bug detection")
    classification_reward: float = Field(default=0.0, description="Reward for correct classification")
    explanation_reward: float = Field(default=0.0, description="Reward for good explanation")
    false_positive_penalty: float = Field(default=0.0, description="Penalty for false positives")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional reward details")

    @validator("score")
    def validate_open_interval_score(cls, value: float) -> float:
        score = float(value)
        if not (0.0 < score < 1.0):
            raise ValueError("score must satisfy 0.0 < score < 1.0")
        return score



class TaskConfig(BaseModel):
    """Configuration for a specific task"""
    task_id: str
    difficulty: str
    code_diff: str
    file_name: str
    language: str
    context: str
    has_bug: bool
    bug_type: Optional[BugType]
    bug_description: Optional[str]
    max_steps: int = 5


class State(BaseModel):
    """Current environment state"""
    current_task: TaskConfig
    step_count: int
    done: bool
    total_reward: float
    history: List[Dict[str, Any]] = Field(default_factory=list)
