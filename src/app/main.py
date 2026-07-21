from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api import products, categories, health
from app.schemas import ErrorResponse
from app.core.database import Base, engine
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Product Catalog Service",
        version="1.0.0",
        description="Backend microservice for managing products and categories with advanced search.",
    )

    # Routers
    app.include_router(health.router)
    app.include_router(categories.router)
    app.include_router(products.router)

    # Error handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(detail=str(exc)).model_dump(),
        )

    @app.on_event("startup")
    async def on_startup():
        # Create tables
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
