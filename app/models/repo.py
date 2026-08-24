from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    repo_name = Column(String, nullable=False)  # e.g. "octocat/hello-world"
    webhook_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="repos")
    pull_requests = relationship(
        "PullRequest", back_populates="repo", cascade="all, delete-orphan"
    )
