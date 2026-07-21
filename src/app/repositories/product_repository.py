from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from sqlalchemy.sql import Select

from .base import IRepository
from app.models import Product, Category, ProductCategory


class IProductRepository(IRepository[Product]):
    def search(
        self,
        keyword: Optional[str],
        category_ids: Optional[List[UUID]],
        min_price: Optional[float],
        max_price: Optional[float],
        skip: int,
        limit: int,
    ) -> Tuple[int, List[Product]]:
        raise NotImplementedError

    def count_search(
        self,
        keyword: Optional[str],
        category_ids: Optional[List[UUID]],
        min_price: Optional[float],
        max_price: Optional[float],
    ) -> int:
        raise NotImplementedError


class ProductRepository(IProductRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, item_id: UUID) -> Optional[Product]:
        return self.db.get(Product, item_id)

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def add(self, item: Product) -> Product:
        self.db.add(item)
        return item

    def update(self, item_id: UUID, item: Product) -> Optional[Product]:
        existing = self.get_by_id(item_id)
        if not existing:
            return None
        for attr in ["name", "description", "price", "sku"]:
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

    def _build_search_query(
        self,
        keyword: Optional[str],
        category_ids: Optional[List[UUID]],
        min_price: Optional[float],
        max_price: Optional[float],
    ) -> Select:
        stmt = (
            select(Product)
            .distinct()
            .join(
                ProductCategory,
                Product.id == ProductCategory.product_id,
                isouter=True,
            )
            .join(
                Category,
                Category.id == ProductCategory.category_id,
                isouter=True,
            )
        )

        conditions = []

        if keyword:
            ts_vector = func.to_tsvector(
                "english",
                func.coalesce(Product.name, "") + " " + func.coalesce(Product.description, ""),
            )
            ts_query = func.plainto_tsquery("english", keyword)
            conditions.append(ts_vector.op("@@")(ts_query))

        if category_ids:
            conditions.append(ProductCategory.category_id.in_(category_ids))

        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        return stmt

    def search(
        self,
        keyword: Optional[str],
        category_ids: Optional[List[UUID]],
        min_price: Optional[float],
        max_price: Optional[float],
        skip: int,
        limit: int,
    ) -> Tuple[int, List[Product]]:
        base_stmt = self._build_search_query(keyword, category_ids, min_price, max_price)

        # total count
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total: int = self.db.execute(count_stmt).scalar_one()

        # page items
        page_stmt = base_stmt.offset(skip).limit(limit)
        items: List[Product] = self.db.execute(page_stmt).scalars().all()

        return total, items

    def count_search(
        self,
        keyword: Optional[str],
        category_ids: Optional[List[UUID]],
        min_price: Optional[float],
        max_price: Optional[float],
    ) -> int:
        stmt = self._build_search_query(keyword, category_ids, min_price, max_price)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return self.db.execute(count_stmt).scalar_one()