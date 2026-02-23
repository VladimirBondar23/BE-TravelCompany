"""
Project SQLAlchemy model.
"""
from sqlalchemy import Column, Date, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    start_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    places = relationship(
        "ProjectPlace",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="joined",
    )
