from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    in_stock: bool = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    in_stock: bool | None = None


class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime


class WSInFrame(BaseModel):
    type: Literal["message", "ping"]
    content: str = ""


class WSOutFrame(BaseModel):
    type: Literal["token", "done", "pong", "error"]
    content: str = ""
