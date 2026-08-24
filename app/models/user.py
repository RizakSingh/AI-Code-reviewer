from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    access_token = Column(String, nullable=False)  # GitHub OAuth token (encrypt at rest in prod)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repos = relationship("Repo", back_populates="owner", cascade="all, delete-orphan")
