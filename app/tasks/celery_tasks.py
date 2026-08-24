import asyncio
import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.pull_request import PullRequest
from app.models.review import Review
from app.models.repo import Repo
from app.models.user import User
from app.services.github_service import get_pr_diff, post_review_comment
from app.services.ai_service import review_diff

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_pr_review(self, pr_id: int):
    """
    Background job: fetch the PR diff, send it to the AI reviewer,
    store the result, and post it back as a GitHub comment.
    Runs outside the webhook request so GitHub's webhook timeout
    (10s) is never at risk.
    """
    db = SessionLocal()
    try:
        pr = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
        if not pr:
            logger.error(f"PullRequest {pr_id} not found")
            return

        pr.status = "reviewing"
        db.commit()

        repo = db.query(Repo).filter(Repo.id == pr.repo_id).first()
        owner = db.query(User).filter(User.id == repo.user_id).first()

        diff = get_pr_diff(owner.access_token, repo.repo_name, pr.pr_number)

        result = asyncio.run(review_diff(diff))

        review = Review(
            pr_id=pr.id,
            ai_summary=result["summary"],
            issues_found=result["issues"],
            suggestions=result["suggestions"],
        )
        db.add(review)

        comment_body = _format_comment(result)
        post_review_comment(owner.access_token, repo.repo_name, pr.pr_number, comment_body)

        pr.status = "reviewed"
        db.commit()

    except Exception as exc:
        db.rollback()
        pr = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
        if pr:
            pr.status = "failed"
            db.commit()
        logger.exception(f"PR review failed for pr_id={pr_id}: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


def _format_comment(result: dict) -> str:
    lines = [f"### 🤖 AI Code Review\n{result['summary']}\n"]

    if result["issues"]:
        lines.append("**Issues found:**")
        for issue in result["issues"]:
            line_ref = f" (line {issue['line']})" if issue.get("line") else ""
            lines.append(f"- `{issue.get('severity', 'info')}`{line_ref}: {issue['message']}")

    if result["suggestions"]:
        lines.append("\n**Suggestions:**")
        for s in result["suggestions"]:
            lines.append(f"- {s}")

    return "\n".join(lines)
