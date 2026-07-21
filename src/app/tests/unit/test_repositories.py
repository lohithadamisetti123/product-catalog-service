from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Product, Category
from app.repositories import ProductRepository, CategoryRepository


def get_test_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_category_repository_crud():
    db = get_test_session()
    repo = CategoryRepository(db)

    cat = Category(name="TestCat", description="Desc")
    repo.add(cat)
    db.commit()

    assert cat.id is not None

    fetched = repo.get_by_id(cat.id)
    assert fetched is not None
    assert fetched.name == "TestCat"

    all_cats = repo.get_all()
    assert len(all_cats) == 1

    deleted = repo.delete(cat.id)
    db.commit()
    assert deleted is True
    assert repo.get_by_id(cat.id) is None


def test_product_repository_crud():
    db = get_test_session()
    cat_repo = CategoryRepository(db)
    prod_repo = ProductRepository(db)

    cat = Category(name="Cat1")
    cat_repo.add(cat)
    db.flush()

    prod = Product(name="Prod1", description="D", price=10, sku="S1", categories=[cat])
    prod_repo.add(prod)
    db.commit()

    fetched = prod_repo.get_by_id(prod.id)
    assert fetched is not None
    assert fetched.sku == "S1"

    fetched_by_sku = prod_repo.get_by_sku("S1")
    assert fetched_by_sku is not None

    all_prods = prod_repo.get_all()
    assert len(all_prods) == 1

    deleted = prod_repo.delete(prod.id)
    db.commit()
    assert deleted is True
