from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False, index=True)
    ai_summary = Column(Text, nullable=True)
    issues_found = Column(JSON, default=list)   # [{"line": int, "severity": str, "message": str}, ...]
    suggestions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pull_request = relationship("PullRequest", back_populates="reviews")
