"""Phase 2 validator checks for deterministic open-interval scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from env.environment import CodeReviewEnv
from env.models import Action, BugType


def main() -> None:
    env = CodeReviewEnv()

    for task in ["easy_off_by_one", "medium_null_check", "hard_sql_injection"]:
        env.reset(task_id=task)

        short_comment_action = Action(
            reviewer_comment="Bug exists here.",
            bug_detected=True,
            bug_type=BugType.LOGIC if task != "hard_sql_injection" else BugType.SECURITY,
        )
        long_comment_action = Action(
            reviewer_comment=(
                "This code introduces a serious bug and the review clearly explains the issue, "
                "pinpoints exact behavior, and proposes a robust fix strategy for safe handling."
            ),
            bug_detected=True,
            bug_type=BugType.LOGIC if task != "hard_sql_injection" else BugType.SECURITY,
        )

        _, reward_a1, _, _ = env.step(short_comment_action)
        env.reset(task_id=task)
        _, reward_a2, _, _ = env.step(short_comment_action)

        env.reset(task_id=task)
        _, reward_b, _, _ = env.step(long_comment_action)

        print(task, reward_a1.score, reward_a2.score, reward_b.score)

        assert 0 < reward_a1.score < 1
        assert 0 < reward_a2.score < 1
        assert 0 < reward_b.score < 1

        assert reward_a1.score == reward_a2.score, f"same input must match for {task}"
        assert reward_a1.score != reward_b.score, f"different comments should differ for {task}"


if __name__ == "__main__":
    main()
