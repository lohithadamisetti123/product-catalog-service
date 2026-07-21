from abc import ABC, abstractmethod
from typing import Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from .product_repository import ProductRepository, IProductRepository
from .category_repository import CategoryRepository, ICategoryRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def products(self) -> IProductRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def categories(self) -> ICategoryRepository:
        raise NotImplementedError

    @abstractmethod
    def begin(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError


class SQLUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None
        self._products: IProductRepository | None = None
        self._categories: ICategoryRepository | None = None

    def __enter__(self) -> "SQLUnitOfWork":
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type:
            self.rollback()
        else:
            try:
                self.commit()
            except Exception:
                self.rollback()
                raise
        self.dispose()

    @property
    def products(self) -> IProductRepository:
        assert self.session is not None
        if self._products is None:
            self._products = ProductRepository(self.session)
        return self._products

    @property
    def categories(self) -> ICategoryRepository:
        assert self.session is not None
        if self._categories is None:
            self._categories = CategoryRepository(self.session)
        return self._categories

    def begin(self) -> None:
        self.session = self._session_factory()
        self.session.begin()

    def commit(self) -> None:
        assert self.session is not None
        self.session.commit()

    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()

    def dispose(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None
            self._products = None
            self._categories = None
