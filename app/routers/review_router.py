from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.pull_request import PullRequest
from app.models.repo import Repo
from app.schemas.review_schema import PullRequestOut

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("/repo/{repo_id}/pull-requests", response_model=List[PullRequestOut])
def list_pull_requests(
    repo_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        raise HTTPException(404, "Repo not found")

    prs = (
        db.query(PullRequest)
        .options(joinedload(PullRequest.reviews))
        .filter(PullRequest.repo_id == repo_id)
        .order_by(PullRequest.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return prs


@router.get("/pull-request/{pr_id}", response_model=PullRequestOut)
def get_pull_request(pr_id: int, db: Session = Depends(get_db)):
    pr = (
        db.query(PullRequest)
        .options(joinedload(PullRequest.reviews))
        .filter(PullRequest.id == pr_id)
        .first()
    )
    if not pr:
        raise HTTPException(404, "Pull request not found")
    return pr


@router.post("/repo")
def register_repo(repo_name: str, user_id: int, db: Session = Depends(get_db)):
    existing = db.query(Repo).filter(Repo.repo_name == repo_name).first()
    if existing:
        raise HTTPException(409, "Repo already registered")

    repo = Repo(user_id=user_id, repo_name=repo_name)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return {"id": repo.id, "repo_name": repo.repo_name}
