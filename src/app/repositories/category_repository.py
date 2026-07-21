from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from .base import IRepository
from app.models import Category


class ICategoryRepository(IRepository[Category]):
    pass


class CategoryRepository(ICategoryRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, item_id: UUID) -> Optional[Category]:
        return self.db.get(Category, item_id)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.db.query(Category).offset(skip).limit(limit).all()

    def add(self, item: Category) -> Category:
        self.db.add(item)
        return item

    def update(self, item_id: UUID, item: Category) -> Optional[Category]:
        existing = self.get_by_id(item_id)
        if not existing:
            return None
        for attr in ["name", "description"]:
            value = getattr(item, attr, None)
            if value is not None:
                setattr(existing, attr, value)
        return existing

    def delete(self, item_id: UUID) -> bool:
        existing = self.get_by_id(item_id)
        if not existing:
            return False
        self.db.delete(existing)
        return True
