from typing import Any, List
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    total: int
    items: List[Any]
