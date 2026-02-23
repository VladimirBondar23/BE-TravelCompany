"""
ProjectPlace SQLAlchemy model.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from models.base import Base


class ProjectPlace(Base):
    __tablename__ = "project_places"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    external_id = Column(String(50), nullable=False)
    title = Column(String(500), nullable=True)
    notes = Column(String(2000), nullable=True)
    visited = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project = relationship("Project", back_populates="places")

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "external_id",
            name="uq_project_place_external_per_project",
        ),
    )
