from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.pull_request import PullRequest
from app.models.repo import Repo
from app.models.user import User
from app.schemas.review_schema import PullRequestOut, RepoCreate, RepoOut

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


def _get_owned_repo(repo_id: int, current_user: User, db: Session) -> Repo:
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        raise HTTPException(404, "Repo not found")
    if repo.user_id != current_user.id:
        raise HTTPException(403, "You do not have access to this repo")
    return repo


@router.get("/repos", response_model=List[RepoOut])
def list_repos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Repo)
        .filter(Repo.user_id == current_user.id)
        .order_by(Repo.created_at.desc())
        .all()
    )


@router.get("/repo/{repo_id}/pull-requests", response_model=List[PullRequestOut])
def list_pull_requests(
    repo_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_repo(repo_id, current_user, db)

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
def get_pull_request(
    pr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pr = (
        db.query(PullRequest)
        .join(Repo, PullRequest.repo_id == Repo.id)
        .options(joinedload(PullRequest.reviews))
        .filter(PullRequest.id == pr_id, Repo.user_id == current_user.id)
        .first()
    )
    if not pr:
        raise HTTPException(404, "Pull request not found")
    return pr


@router.post("/repo", response_model=RepoOut, status_code=201)
def register_repo(
    body: RepoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Repo).filter(Repo.repo_name == body.repo_name).first()
    if existing:
        raise HTTPException(409, "Repo already registered")

    repo = Repo(user_id=current_user.id, repo_name=body.repo_name)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo
