from sqlalchemy import Column, Text, Numeric, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    sku = Column(Text, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)

    categories = relationship(
        "Category",
        secondary="product_categories",
        back_populates="products",
    )
