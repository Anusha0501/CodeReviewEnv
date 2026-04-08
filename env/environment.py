"""Main CodeReviewEnv implementation following OpenEnv specification"""

import random
from typing import Dict, List, Optional, Tuple, Any
from .models import Observation, Action, Reward, State, TaskConfig
from .tasks import TaskManager, TaskGrader


class CodeReviewEnv:
    """
    AI-Powered Code Review & Bug Detection Environment
    
    This environment simulates a developer reviewing code diffs and identifying
    bugs, issues, and improvements in pull requests.
    """
    
    def __init__(self, task_id: Optional[str] = None, difficulty: Optional[str] = None):
        """
        Initialize the environment
        
        Args:
            task_id: Specific task ID to load (if None, random task selected)
            difficulty: Difficulty level to filter tasks (easy, medium, hard)
        """
        self.task_manager = TaskManager()
        self.grader = TaskGrader()
        self._state: Optional[State] = None
        self.max_steps = 5
        
        # Initialize with a task
        self._initialize_task(task_id, difficulty)
    
    def _initialize_task(self, task_id: Optional[str] = None, difficulty: Optional[str] = None):
        """Initialize environment with a specific task"""
        if task_id:
            task = self.task_manager.get_task(task_id)
            if not task:
                raise ValueError(f"Task '{task_id}' not found")
        elif difficulty:
            tasks = self.task_manager.get_tasks_by_difficulty(difficulty)
            if not tasks:
                raise ValueError(f"No tasks found for difficulty '{difficulty}'")
            task = random.choice(tasks)
        else:
            # Random task from all available
            all_tasks = list(self.task_manager.get_all_tasks().values())
            task = random.choice(all_tasks)
        
        self._state = State(
            current_task=task,
            step_count=0,
            done=False,
            total_reward=0.0,
            history=[]
        )
    
    def reset(self, task_id: Optional[str] = None, difficulty: Optional[str] = None) -> Observation:
        """
        Reset the environment and return initial observation
        
        Args:
            task_id: Specific task ID to load (if None, random task selected)
            difficulty: Difficulty level to filter tasks
            
        Returns:
            Initial observation
        """
        self._initialize_task(task_id, difficulty)
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Execute one step in the environment
        
        Args:
            action: The reviewer action to take
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        if self._state is None or self._state.done:
            raise RuntimeError("Environment not initialized or already finished. Call reset() first.")
        
        # Grade the action
        reward = self.grader.grade_action(action, self._state.current_task, self._state.step_count)
        
        # Update state
        self._state.step_count += 1
        self._state.total_reward += reward.score
        self._state.history.append({
            "step": self._state.step_count,
            "action": action.dict(),
            "reward": reward.dict()
        })
        
        # Check if done
        done = self._state.step_count >= self._state.current_task.max_steps or reward.score >= 0.8
        self._state.done = done
        
        # Get observation
        observation = self._get_observation()
        
        # Info dictionary
        info = {
            "task_id": self._state.current_task.task_id,
            "difficulty": self._state.current_task.difficulty,
            "total_steps": self._state.step_count,
            "task_completed": reward.score >= 0.8
        }
        
        return observation, reward, done, info
    
    def state(self) -> Dict[str, Any]:
        """
        Get current state as dictionary (OpenEnv required method)
        
        Returns:
            Current state dictionary
        """
        if self._state is None:
            return {}
        
        return {
            "current_task": self._state.current_task.dict(),
            "step_count": self._state.step_count,
            "done": self._state.done,
            "total_reward": self._state.total_reward,
            "history": self._state.history
        }
    
    def state_dict(self) -> Dict[str, Any]:
        """
        Get current state as dictionary (backward compatibility)
        
        Returns:
            Current state dictionary
        """
        return self.state()
    
    def _get_observation(self) -> Observation:
        """Generate current observation from state"""
        if self._state is None:
            raise RuntimeError("Environment not initialized")
        
        # Extract previous comments from history
        previous_comments = []
        for entry in self._state.history:
            comment = entry["action"]["reviewer_comment"]
            previous_comments.append(comment)
        
        return Observation(
            code_diff=self._state.current_task.code_diff,
            file_name=self._state.current_task.file_name,
            language=self._state.current_task.language,
            context=self._state.current_task.context,
            previous_comments=previous_comments,
            step_count=self._state.step_count
        )
    
    def get_task_info(self) -> Dict[str, Any]:
        """Get information about the current task"""
        if self._state is None:
            return {}
        
        return {
            "task_id": self._state.current_task.task_id,
            "difficulty": self._state.current_task.difficulty,
            "file_name": self._state.current_task.file_name,
            "language": self._state.current_task.language,
            "has_bug": self._state.current_task.has_bug,
            "bug_type": self._state.current_task.bug_type.value if self._state.current_task.bug_type else None,
            "max_steps": self._state.current_task.max_steps
        }
    
    def list_available_tasks(self) -> Dict[str, Dict[str, Any]]:
        """List all available tasks"""
        tasks = {}
        for task_id, task in self.task_manager.get_all_tasks().items():
            tasks[task_id] = {
                "difficulty": task.difficulty,
                "file_name": task.file_name,
                "language": task.language,
                "has_bug": task.has_bug
            }
        return tasks
    
    def render(self, mode: str = "human") -> Optional[str]:
        """
        Render the environment for visualization
        
        Args:
            mode: Rendering mode ('human' or 'ansi')
            
        Returns:
            Rendered environment string or None
        """
        if self._state is None:
            return None
        
        output = []
        output.append(f"=== Code Review Environment ===")
        output.append(f"Task: {self._state.current_task.task_id} ({self._state.current_task.difficulty})")
        output.append(f"File: {self._state.current_task.file_name}")
        output.append(f"Step: {self._state.step_count}/{self._state.current_task.max_steps}")
        output.append(f"Total Reward: {self._state.total_reward:.3f}")
        output.append("")
        output.append("Code Diff:")
        output.append(self._state.current_task.code_diff)
        output.append("")
        
        if self._state.history:
            output.append("Previous Comments:")
            for i, entry in enumerate(self._state.history, 1):
                output.append(f"{i}. {entry['action']['reviewer_comment']}")
        
        return "\n".join(output) if mode == "ansi" else print("\n".join(output))
