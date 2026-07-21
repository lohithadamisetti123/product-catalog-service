from typing import Optional, List
from pydantic import BaseModel, Field, condecimal
from uuid import UUID
from .category import CategoryInDB


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    sku: str = Field(..., min_length=1, max_length=255)


class ProductCreate(ProductBase):
    category_ids: Optional[List[UUID]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2)]  # type: ignore
    sku: Optional[str] = Field(None, min_length=1, max_length=255)
    category_ids: Optional[List[UUID]] = None


class ProductInDB(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    price: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    sku: str

    class Config:
        from_attributes = True


class ProductWithCategories(ProductInDB):
    categories: List[CategoryInDB]
