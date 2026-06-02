from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ScanCreate(BaseModel):
    barcode: str
    child_id: UUID

class ScanResponse(BaseModel):
    id: UUID
    child_id: UUID
    barcode: str
    product_name: str
    nutriscore: Optional[str] = None
    color_rating: str
    is_alcohol: bool
    scanned_at: datetime

    class Config:
        from_attributes = True