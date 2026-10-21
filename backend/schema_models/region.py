from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import ORMBase


class RegionBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class Region(RegionBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


__all__ = [
    "RegionBase",
    "RegionCreate",
    "RegionUpdate",
    "Region",
]
