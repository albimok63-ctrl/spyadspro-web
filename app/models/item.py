"""
Item model – Pydantic v2 schemas for request/response and domain.
No HTTP, no FastAPI-specific code.
"""

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Shared fields for Item."""

    name: str = Field(..., min_length=1)
    description: str = ""


class ItemCreate(ItemBase):
    """Request body for creating an Item (no id)."""

    pass


class ItemRead(ItemBase):
    """Response/read model for Item (with id)."""

    id: int

    model_config = {"from_attributes": True}


class ItemModel(ItemBase):
    """Domain model with id – used by repository/service internally."""

    id: int

    model_config = {"from_attributes": True}
