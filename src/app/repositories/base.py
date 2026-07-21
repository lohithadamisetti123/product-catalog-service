from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, item_id) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def add(self, item: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, item_id, item: T) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id) -> bool:
        raise NotImplementedError
