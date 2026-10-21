from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import ORMBase


class ChannelBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class Channel(ChannelBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


__all__ = [
    "ChannelBase",
    "ChannelCreate",
    "ChannelUpdate",
    "Channel",
]
