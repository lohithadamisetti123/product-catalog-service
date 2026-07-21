from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
