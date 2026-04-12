import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Phase 2 validator check for score range and variability."""

from env.environment import CodeReviewEnv
from env.models import Action, BugType


def main() -> None:
    env = CodeReviewEnv()

    sample_actions = {
        "easy_off_by_one": Action(
            reviewer_comment="There is an off-by-one bug in the loop that can raise an index error on the final iteration.",
            bug_detected=True,
            bug_type=BugType.LOGIC,
        ),
        "medium_null_check": Action(
            reviewer_comment="This function accesses user.name without a null check, which can trigger an attribute error.",
            bug_detected=True,
            bug_type=BugType.LOGIC,
        ),
        "hard_sql_injection": Action(
            reviewer_comment="The query uses direct interpolation and enables SQL injection; use parameterized execution.",
            bug_detected=True,
            bug_type=BugType.SECURITY,
        ),
    }

    for task in ["easy_off_by_one", "medium_null_check", "hard_sql_injection"]:
        env.reset(task_id=task)
        scores = []

        for _ in range(5):
            _, reward, _, _ = env.step(sample_actions[task])
            scores.append(reward.score)

        print(task, scores)

        assert all(0 < s < 1 for s in scores), f"score out of open interval for {task}: {scores}"
        assert len(set(scores)) > 1, f"scores are not varying for {task}: {scores}"


if __name__ == "__main__":
    main()
