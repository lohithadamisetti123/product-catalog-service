from typing import List, Optional
from uuid import UUID

from app.repositories.unit_of_work import IUnitOfWork
from app.schemas import CategoryCreate, CategoryUpdate, CategoryInDB
from app.models import Category


class CategoryService:
    def __init__(self, uow_factory):
        self._uow_factory = uow_factory

    def create_category(self, data: CategoryCreate) -> CategoryInDB:
        with self._uow_factory() as uow:
            existing = uow.categories.get_by_name(data.name)
            if existing:
                raise ValueError("Category with this name already exists")
            entity = Category(name=data.name, description=data.description)
            uow.categories.add(entity)
            return CategoryInDB.model_validate(entity)

    def get_category(self, category_id: UUID) -> Optional[CategoryInDB]:
        with self._uow_factory() as uow:
            category = uow.categories.get_by_id(category_id)
            return CategoryInDB.model_validate(category) if category else None

    def list_categories(self, skip: int = 0, limit: int = 100) -> list[CategoryInDB]:
        with self._uow_factory() as uow:
            cats = uow.categories.get_all(skip=skip, limit=limit)
            return [CategoryInDB.model_validate(c) for c in cats]

    def update_category(self, category_id: UUID, data: CategoryUpdate) -> Optional[CategoryInDB]:
        with self._uow_factory() as uow:
            existing = uow.categories.get_by_id(category_id)
            if not existing:
                return None
            if data.name is not None:
                existing.name = data.name
            if data.description is not None:
                existing.description = data.description
            return CategoryInDB.model_validate(existing)

    def delete_category(self, category_id: UUID) -> bool:
        with self._uow_factory() as uow:
            return uow.categories.delete(category_id)
