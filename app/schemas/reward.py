from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RewardResponse(BaseModel):
    id: UUID
    child_id: UUID
    scan_id: Optional[UUID] = None
    reward_type: str
    content: Optional[str] = None
    is_unlocked: bool
    unlocked_at: Optional[datetime] = None

    class Config:
        from_attributes = True