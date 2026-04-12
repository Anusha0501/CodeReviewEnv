"""Task definitions and graders for CodeReviewEnv"""

import random
import re
from typing import Dict, List, Optional
from .models import TaskConfig, Action, Reward, BugType


class TaskGrader:
    """Deterministic grader for code review tasks"""

    @staticmethod
    def grade_action(action: Action, task: TaskConfig, step: int) -> Reward:
        """Grade an action against the task ground truth with deterministic open-interval scoring."""
        score = 0.1

        correct_detection = action.bug_detected == task.has_bug
        correct_bug_type = bool(action.bug_detected and task.has_bug and action.bug_type == task.bug_type)
        false_positive = bool((task.has_bug is False) and (action.bug_detected is True))

        explanation_reward = TaskGrader._evaluate_explanation(action.reviewer_comment)

        if correct_detection:
            score += 0.3
        if correct_bug_type:
            score += 0.2

        score += explanation_reward

        # Add deterministic variation based on comment keywords
        comment = action.reviewer_comment.lower()
        if "error" in comment:
            score += 0.03
        if "fix" in comment:
            score += 0.02
        if "line" in comment:
            score += 0.02

        if not task.has_bug and not action.bug_detected:
            score += 0.3

        if false_positive:
            score -= 0.2

        if score <= 0:
            score = 0.05
        elif score >= 1:
            score = 0.95

        score = max(0.05, min(score, 0.95))

        detection_reward = 0.3 if correct_detection else 0.05
        classification_reward = 0.2 if correct_bug_type else 0.05
        false_positive_penalty = 0.2 if false_positive else 0.05

        return Reward(
            score=float(score),
            detection_reward=float(detection_reward),
            classification_reward=float(classification_reward),
            explanation_reward=float(explanation_reward),
            false_positive_penalty=float(false_positive_penalty),
            details={
                "correct_detection": correct_detection,
                "correct_classification": correct_bug_type if task.has_bug else None,
                "comment_word_count": len(action.reviewer_comment.split()),
                "false_positive": false_positive,
                "step": step,
            },
        )

    @staticmethod
    def _evaluate_explanation(comment: str) -> float:
        """Evaluate explanation quality deterministically using comment word count."""
        comment_length = len(comment.split())

        if comment_length > 20:
            return 0.3
        if comment_length > 10:
            return 0.2
        if comment_length > 5:
            return 0.1
        return 0.05


# Task definitions
EASY_TASK = TaskConfig(
    task_id="easy_off_by_one",
    difficulty="easy",
    code_diff="""@@ -1,7 +1,7 @@
def calculate_average(numbers):
-    total = sum(numbers)
-    return total / len(numbers)
+    total = sum(numbers)
+    for i in range(len(numbers) + 1):  # Off-by-one error
+        total += numbers[i]
+    return total / len(numbers)""",
    file_name="math_utils.py",
    language="python",
    context="Function to calculate average of a list of numbers",
    has_bug=True,
    bug_type=BugType.LOGIC,
    bug_description="Off-by-one error in loop causing IndexError"
)

MEDIUM_TASK = TaskConfig(
    task_id="medium_null_check",
    difficulty="medium",
    code_diff="""@@ -1,8 +1,8 @@
def process_user_data(user):
-    if user is not None:
-        return user.name.upper()
-    else:
-        return \"Unknown\"
+    # Simplified logic
+    return user.name.upper()  # Missing null check""",
    file_name="user_service.py",
    language="python",
    context="Process user data and return formatted name",
    has_bug=True,
    bug_type=BugType.LOGIC,
    bug_description="Missing null check will cause AttributeError"
)

HARD_TASK = TaskConfig(
    task_id="hard_sql_injection",
    difficulty="hard",
    code_diff="""@@ -1,8 +1,8 @@
def get_user_by_id(user_id):
-    query = \"SELECT * FROM users WHERE id = %s\"
-    cursor.execute(query, (user_id,))
-    return cursor.fetchone()
+    # Direct string interpolation for simplicity
+    query = f\"SELECT * FROM users WHERE id = {user_id}\"
+    cursor.execute(query)
+    return cursor.fetchone()""",
    file_name="database.py",
    language="python",
    context="Retrieve user from database by ID",
    has_bug=True,
    bug_type=BugType.SECURITY,
    bug_description="SQL injection vulnerability through string interpolation"
)

# Clean tasks (no bugs)
CLEAN_TASK_EASY = TaskConfig(
    task_id="clean_easy",
    difficulty="easy",
    code_diff="""@@ -1,4 +1,4 @@
-def add(a, b):
-    return a + b
+def add_numbers(a, b):
+    return a + b""",
    file_name="calculator.py",
    language="python",
    context="Simple addition function renamed for clarity",
    has_bug=False,
    bug_type=None,
    bug_description=None
)

CLEAN_TASK_MEDIUM = TaskConfig(
    task_id="clean_medium",
    difficulty="medium",
    code_diff="""@@ -1,6 +1,6 @@
def validate_email(email):
-    return \"@\" in email
+    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
+    return re.match(pattern, email) is not None""",
    file_name="validators.py",
    language="python",
    context="Email validation function improved with regex",
    has_bug=False,
    bug_type=None,
    bug_description=None
)


class TaskManager:
    """Manages available tasks and selection"""

    def __init__(self):
        self.tasks = {
            "easy_off_by_one": EASY_TASK,
            "medium_null_check": MEDIUM_TASK,
            "hard_sql_injection": HARD_TASK,
            "clean_easy": CLEAN_TASK_EASY,
            "clean_medium": CLEAN_TASK_MEDIUM,
        }

    def get_task(self, task_id: str) -> Optional[TaskConfig]:
        """Get a specific task by ID"""
        return self.tasks.get(task_id)

    def get_tasks_by_difficulty(self, difficulty: str) -> List[TaskConfig]:
        """Get all tasks of a specific difficulty"""
        return [task for task in self.tasks.values() if task.difficulty == difficulty]

    def get_all_tasks(self) -> Dict[str, TaskConfig]:
        """Get all available tasks"""
        return self.tasks.copy()
