from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.schemas import CategoryCreate, CategoryUpdate, CategoryInDB, ErrorResponse
from app.repositories.unit_of_work import IUnitOfWork
from .deps import get_uow

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryInDB,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_category(payload: CategoryCreate, uow: IUnitOfWork = Depends(get_uow)):
    from app.models import Category

    existing = uow.categories.get_by_name(payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    category = Category(name=payload.name, description=payload.description)
    uow.categories.add(category)
    return CategoryInDB.model_validate(category)


@router.get(
    "/{category_id}",
    response_model=CategoryInDB,
    responses={404: {"model": ErrorResponse}},
)
def get_category(category_id: UUID, uow: IUnitOfWork = Depends(get_uow)):
    category = uow.categories.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryInDB.model_validate(category)


@router.get("", response_model=list[CategoryInDB])
def list_categories(skip: int = 0, limit: int = 100, uow: IUnitOfWork = Depends(get_uow)):
    categories = uow.categories.get_all(skip=skip, limit=limit)
    return [CategoryInDB.model_validate(c) for c in categories]


@router.put(
    "/{category_id}",
    response_model=CategoryInDB,
    responses={404: {"model": ErrorResponse}},
)
def update_category(category_id: UUID, payload: CategoryUpdate, uow: IUnitOfWork = Depends(get_uow)):
    category = uow.categories.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.name is not None:
        category.name = payload.name
    if payload.description is not None:
        category.description = payload.description

    return CategoryInDB.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_category(category_id: UUID, uow: IUnitOfWork = Depends(get_uow)):
    deleted = uow.categories.delete(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return None
