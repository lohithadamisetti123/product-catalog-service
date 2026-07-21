import decimal
from app.core.database import SessionLocal, engine, Base
from app.models import Category, Product


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Category).count() > 0:
            return

        cat_electronics = Category(name="Electronics", description="Electronic gadgets")
        cat_books = Category(name="Books", description="Books and literature")
        cat_clothing = Category(name="Clothing", description="Apparel and accessories")

        db.add_all([cat_electronics, cat_books, cat_clothing])
        db.flush()

        products = [
            Product(name="Smartphone X", description="High-end smartphone", price=decimal.Decimal("699.99"), sku="SKU-001", categories=[cat_electronics]),
            Product(name="Laptop Pro", description="Powerful laptop", price=decimal.Decimal("1299.99"), sku="SKU-002", categories=[cat_electronics]),
            Product(name="Wireless Headphones", description="Noise cancelling", price=decimal.Decimal("199.99"), sku="SKU-003", categories=[cat_electronics]),
            Product(name="Sci-Fi Novel", description="A sci-fi bestseller", price=decimal.Decimal("19.99"), sku="SKU-004", categories=[cat_books]),
            Product(name="Programming Book", description="Learn Python", price=decimal.Decimal("39.99"), sku="SKU-005", categories=[cat_books]),
            Product(name="T-Shirt", description="Cotton t-shirt", price=decimal.Decimal("9.99"), sku="SKU-006", categories=[cat_clothing]),
            Product(name="Jeans", description="Blue denim", price=decimal.Decimal("49.99"), sku="SKU-007", categories=[cat_clothing]),
            Product(name="Sneakers", description="Comfortable sneakers", price=decimal.Decimal("89.99"), sku="SKU-008", categories=[cat_clothing]),
            Product(name="E-reader", description="E-ink reader", price=decimal.Decimal("129.99"), sku="SKU-009", categories=[cat_electronics, cat_books]),
            Product(name="Hoodie", description="Warm hoodie", price=decimal.Decimal("59.99"), sku="SKU-010", categories=[cat_clothing]),
        ]

        db.add_all(products)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
