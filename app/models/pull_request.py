from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False, index=True)
    pr_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending | reviewing | reviewed | failed
    delivery_id = Column(String, unique=True, index=True, nullable=True)  # GitHub webhook delivery id, for idempotency
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repo = relationship("Repo", back_populates="pull_requests")
    reviews = relationship(
        "Review", back_populates="pull_request", cascade="all, delete-orphan"
    )
