from typing import Generator
from app.repositories.unit_of_work import SQLUnitOfWork, IUnitOfWork


def get_uow() -> Generator[IUnitOfWork, None, None]:
    uow = SQLUnitOfWork()
    try:
        uow.begin()
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise
    finally:
        uow.dispose()
