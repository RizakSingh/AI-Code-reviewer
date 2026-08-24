from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Issue(BaseModel):
    line: Optional[int] = None
    severity: str = "info"  # info | warning | critical
    message: str


class ReviewOut(BaseModel):
    id: int
    ai_summary: Optional[str] = None
    issues_found: List[Issue] = []
    suggestions: List[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class PullRequestOut(BaseModel):
    id: int
    pr_number: int
    title: str
    author: str
    status: str
    reviews: List[ReviewOut] = []

    model_config = {"from_attributes": True}
