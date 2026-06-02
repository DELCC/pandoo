import uuid
from sqlalchemy import String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Child(Base):
    __tablename__ = "children"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=False)
    allergens: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="children")
    scans: Mapped[list["Scan"]] = relationship("Scan", back_populates="child")
    rewards: Mapped[list["Reward"]] = relationship("Reward", back_populates="child")