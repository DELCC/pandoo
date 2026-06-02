import uuid
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id"), nullable=False)
    barcode: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    nutriscore: Mapped[str] = mapped_column(String(1), nullable=True)
    color_rating: Mapped[str] = mapped_column(String(10), nullable=False)
    is_alcohol: Mapped[bool] = mapped_column(Boolean, default=False)
    scanned_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    child: Mapped["Child"] = relationship("Child", back_populates="scans")
    reward: Mapped["Reward"] = relationship("Reward", back_populates="scan")