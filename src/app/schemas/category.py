from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryInDB(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True  # pydantic v2
