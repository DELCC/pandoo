from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class ChildCreate(BaseModel):
    first_name: str
    birth_date: date
    allergens: Optional[str] = None

class ChildResponse(BaseModel):
    id: UUID
    first_name: str
    birth_date: date
    allergens: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True