from fastapi import APIRouter, Request, Header, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.database import get_db
from app.models.repo import Repo
from app.models.pull_request import PullRequest
from app.services.webhook_security import verify_signature
from app.tasks.celery_tasks import process_pr_review

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    x_github_delivery: str = Header(None),
):
    raw_body = await request.body()

    if not verify_signature(raw_body, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(401, "Invalid webhook signature")

    # Respond fast to anything we don't care about - GitHub sends many event types.
    if x_github_event != "pull_request":
        return {"status": "ignored", "reason": f"event type {x_github_event} not handled"}

    payload = await request.json()
    action = payload.get("action")

    if action not in ("opened", "synchronize", "reopened"):
        return {"status": "ignored", "reason": f"action {action} not handled"}

    # Idempotency: GitHub retries webhook deliveries on timeout/failure.
    # If we've already recorded this delivery id, don't reprocess.
    existing = db.query(PullRequest).filter(PullRequest.delivery_id == x_github_delivery).first()
    if existing:
        return {"status": "duplicate", "pr_id": existing.id}

    repo_full_name = payload["repository"]["full_name"]
    repo = db.query(Repo).filter(Repo.repo_name == repo_full_name).first()
    if not repo:
        raise HTTPException(404, f"Repo {repo_full_name} is not registered with this app")

    pr_data = payload["pull_request"]
    pr = PullRequest(
        repo_id=repo.id,
        pr_number=pr_data["number"],
        title=pr_data["title"],
        author=pr_data["user"]["login"],
        status="pending",
        delivery_id=x_github_delivery,
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)

    # Enqueue background job and return immediately - keeps webhook
    # response well under GitHub's timeout even if the LLM call is slow.
    process_pr_review.delay(pr.id)

    return {"status": "queued", "pr_id": pr.id}
