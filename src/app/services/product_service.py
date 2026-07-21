from typing import List, Optional
from uuid import UUID

from app.repositories.unit_of_work import IUnitOfWork
from app.schemas import ProductCreate, ProductUpdate, ProductWithCategories
from app.models import Product, Category


class ProductService:
    def __init__(self, uow_factory):
        self._uow_factory = uow_factory

    def create_product(self, data: ProductCreate) -> ProductWithCategories:
        with self._uow_factory() as uow:
            if uow.products.get_by_sku(data.sku):
                raise ValueError("Product with this SKU already exists")

            product = Product(
                name=data.name,
                description=data.description,
                price=data.price,
                sku=data.sku,
            )

            if data.category_ids:
                categories: List[Category] = []
                for cid in data.category_ids:
                    cat = uow.categories.get_by_id(cid)
                    if not cat:
                        raise ValueError(f"Category {cid} not found")
                    categories.append(cat)
                product.categories = categories

            uow.products.add(product)
            return ProductWithCategories.model_validate(product)

    def get_product(self, product_id: UUID) -> Optional[ProductWithCategories]:
        with self._uow_factory() as uow:
            product = uow.products.get_by_id(product_id)
            if not product:
                return None
            return ProductWithCategories.model_validate(product)

    def list_products(self, skip: int = 0, limit: int = 10) -> List[ProductWithCategories]:
        with self._uow_factory() as uow:
            products = uow.products.get_all(skip=skip, limit=limit)
            return [ProductWithCategories.model_validate(p) for p in products]

    def update_product(self, product_id: UUID, data: ProductUpdate) -> Optional[ProductWithCategories]:
        with self._uow_factory() as uow:
            product = uow.products.get_by_id(product_id)
            if not product:
                return None

            if data.sku and data.sku != product.sku:
                if uow.products.get_by_sku(data.sku):
                    raise ValueError("Product with this SKU already exists")

            if data.name is not None:
                product.name = data.name
            if data.description is not None:
                product.description = data.description
            if data.price is not None:
                product.price = data.price
            if data.sku is not None:
                product.sku = data.sku

            if data.category_ids is not None:
                categories: List[Category] = []
                for cid in data.category_ids:
                    cat = uow.categories.get_by_id(cid)
                    if not cat:
                        raise ValueError(f"Category {cid} not found")
                    categories.append(cat)
                product.categories = categories

            return ProductWithCategories.model_validate(product)

    def delete_product(self, product_id: UUID) -> bool:
        with self._uow_factory() as uow:
            return uow.products.delete(product_id)

    def search_products(
        self,
        keyword: Optional[str],
        category_ids: Optional[List[UUID]],
        min_price: Optional[float],
        max_price: Optional[float],
        skip: int,
        limit: int,
    ):
        with self._uow_factory() as uow:
            items = uow.products.search(
                keyword=keyword,
                category_ids=category_ids,
                min_price=min_price,
                max_price=max_price,
                skip=skip,
                limit=limit,
            )
            total = uow.products.count_search(
                keyword=keyword,
                category_ids=category_ids,
                min_price=min_price,
                max_price=max_price,
            )
            return total, [ProductWithCategories.model_validate(p) for p in items]
