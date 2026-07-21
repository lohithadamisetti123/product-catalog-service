from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductWithCategories,
    ErrorResponse,
    PaginatedResponse,
)
from app.repositories.unit_of_work import IUnitOfWork
from .deps import get_uow
from app.models import Product, Category

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=ProductWithCategories,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_product(payload: ProductCreate, uow: IUnitOfWork = Depends(get_uow)):
    if uow.products.get_by_sku(payload.sku):
        raise HTTPException(
            status_code=400, detail="Product with this SKU already exists"
        )

    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        sku=payload.sku,
    )

    if payload.category_ids:
        categories: List[Category] = []
        for cid in payload.category_ids:
            cat = uow.categories.get_by_id(cid)
            if not cat:
                raise HTTPException(
                    status_code=400, detail=f"Category {cid} not found"
                )
            categories.append(cat)
        product.categories = categories

    uow.products.add(product)
    return ProductWithCategories.model_validate(product)


@router.get("", response_model=PaginatedResponse)
def list_products(
    skip: int = 0,
    limit: int = 10,
    uow: IUnitOfWork = Depends(get_uow),
):
    products = uow.products.get_all(skip=skip, limit=limit)
    items = [ProductWithCategories.model_validate(p) for p in products]
    total = skip + len(items)
    return PaginatedResponse(total=total, items=items)


@router.get("/search", response_model=PaginatedResponse)
def search_products(
    q: Optional[str] = Query(default=None),
    category_ids: Optional[List[UUID]] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    skip: int = 0,
    limit: int = 10,
    uow: IUnitOfWork = Depends(get_uow),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400, detail="min_price cannot be greater than max_price"
        )

    total, products = uow.products.search(
        keyword=q,
        category_ids=category_ids,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit,
    )

    items = [ProductWithCategories.model_validate(p) for p in products]
    return PaginatedResponse(total=total, items=items)


@router.get(
    "/{product_id}",
    response_model=ProductWithCategories,
    responses={404: {"model": ErrorResponse}},
)
def get_product(product_id: UUID, uow: IUnitOfWork = Depends(get_uow)):
    product = uow.products.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductWithCategories.model_validate(product)


@router.put(
    "/{product_id}",
    response_model=ProductWithCategories,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
def update_product(
    product_id: UUID, payload: ProductUpdate, uow: IUnitOfWork = Depends(get_uow)
):
    product = uow.products.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.sku and payload.sku != product.sku:
        if uow.products.get_by_sku(payload.sku):
            raise HTTPException(
                status_code=400, detail="Product with this SKU already exists"
            )

    if payload.name is not None:
        product.name = payload.name
    if payload.description is not None:
        product.description = payload.description
    if payload.price is not None:
        product.price = payload.price
    if payload.sku is not None:
        product.sku = payload.sku

    if payload.category_ids is not None:
        categories: List[Category] = []
        for cid in payload.category_ids:
            cat = uow.categories.get_by_id(cid)
            if not cat:
                raise HTTPException(
                    status_code=400, detail=f"Category {cid} not found"
                )
            categories.append(cat)
        product.categories = categories

    return ProductWithCategories.model_validate(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_product(product_id: UUID, uow: IUnitOfWork = Depends(get_uow)):
    deleted = uow.products.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return None