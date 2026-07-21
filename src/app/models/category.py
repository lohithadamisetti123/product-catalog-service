from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories",
    )
