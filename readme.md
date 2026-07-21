# Product Catalog Service

A simple **Product Catalog Service** built with FastAPI, SQLAlchemy, and PostgreSQL, containerized with Docker and orchestrated using Docker Compose.

This project implements a small, production‑style backend API for managing products and categories, including full CRUD operations, many‑to‑many relationships, and a flexible search endpoint with pagination and filtering.

---

## Features

- FastAPI‑based REST API.
- PostgreSQL as the persistence layer.
- SQLAlchemy ORM models and sessions.
- Repository and Unit of Work patterns.
- Products and Categories with a many‑to‑many relationship.
- Pagination and filtering for listing and search.
- Full‑text search on product name and description (PostgreSQL).
- Docker and Docker Compose for easy setup.
- Database schema auto‑creation at startup.
- Seed data for quick testing.
- OpenAPI / Swagger documentation at `/docs`.
- Basic health check endpoint at `/health`.

---

## Architecture Overview

The service is structured into the following main layers:

- **API layer** (`src/app/api`): FastAPI routers and request/response models.
- **Schemas** (`src/app/schemas`): Pydantic models for validation and serialization.
- **Models** (`src/app/models`): SQLAlchemy ORM models representing database tables.
- **Repositories** (`src/app/repositories`): Data access layer encapsulating DB interaction.
- **Unit of Work** (`src/app/repositories/unit_of_work.py`): Manages transactions and repository instances.
- **Main application** (`src/app/main.py`): FastAPI app setup, DB engine, and startup logic.

The design follows a clean separation of concerns so that the API layer depends on repository interfaces rather than on raw ORM queries.

---

## Data Model

The core entities are:

- **Category**
  - `id` (UUID primary key)
  - `name`
  - `description`

- **Product**
  - `id` (UUID primary key)
  - `name`
  - `description`
  - `price` (decimal)
  - `sku` (unique)
  - Many‑to‑many relationship to `Category` via a join table.

The join table is typically called `product_categories` (or similar) and links products to categories through their IDs.

Seed data is inserted on startup (via SQL or startup logic) to provide:

- A few default categories: Electronics, Books, Clothing.
- Several products distributed across these categories.

---

## API Endpoints

### Health

- `GET /health`  
  Returns a simple JSON status to indicate that the application is running and the database is reachable.

Example response:

```json
{"status": "UP"}
```

---

### Category Endpoints

- `GET /categories`  
  List all categories.

- `POST /categories`  
  Create a new category.

- `GET /categories/{category_id}`  
  Retrieve a single category by ID.

- `PUT /categories/{category_id}`  
  Update a category.

- `DELETE /categories/{category_id}`  
  Delete a category.

These endpoints use Pydantic schemas for validation and return JSON representations of categories.

---

### Product Endpoints

- `GET /products`  
  List products with pagination.

  Query parameters:
  - `skip` (int, default 0)
  - `limit` (int, default 10)

  Response shape:

  ```json
  {
    "total": 10,
    "items": [
      {
        "id": "...",
        "name": "Smartphone X",
        "description": "High-end smartphone",
        "price": "699.99",
        "sku": "SKU-001",
        "categories": [
          {
            "id": "...",
            "name": "Electronics",
            "description": "Electronic gadgets"
          }
        ]
      }
    ]
  }
  ```

- `POST /products`  
  Create a new product with optional category assignments.

- `GET /products/{product_id}`  
  Retrieve a single product by ID, including its categories.

- `PUT /products/{product_id}`  
  Update a product’s fields and categories.

- `DELETE /products/{product_id}`  
  Delete a product by ID.

---

### Product Search

- `GET /products/search`  

Provides keyword search and filtering over products, with pagination.

Query parameters:

- `q` (optional string): Keyword to search in product name and description. Implemented using PostgreSQL full‑text search.
- `category_ids` (optional list of UUIDs): Filter to products that belong to any of the given categories.
- `min_price` (optional float): Minimum price.
- `max_price` (optional float): Maximum price.
- `skip` (int, default 0): Items to skip (offset).
- `limit` (int, default 10): Maximum items to return.

Validation:

- If both `min_price` and `max_price` are provided, `min_price` must not be greater than `max_price`.

Response:

```json
{
  "total": 1,
  "items": [
    {
      "id": "2ef0168b-ed92-4266-b733-0ef486baa523",
      "name": "Programming Book",
      "description": "Learn Python",
      "price": "39.99",
      "sku": "SKU-005",
      "categories": [
        {
          "id": "4a8be647-e70e-4b7b-beed-4b71ade2376d",
          "name": "Books",
          "description": "Books and literature"
        }
      ]
    }
  ]
}
```

---

## Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Start the stack

From the project root:

```bash
docker-compose down
docker-compose up --build
```

This will:

- Start a PostgreSQL container with the `product_catalog` database.
- Initialize the schema using `schema.sql`.
- Start the FastAPI application container.
- Wait for the DB to become healthy before starting the app.

Once the services are up, the API is available at:

- `http://localhost:8000`

---

## Verifying the API

With the stack running, you can test endpoints using `curl`:

```bash
# Health
curl "http://localhost:8000/health"

# List categories
curl "http://localhost:8000/categories"

# List products
curl "http://localhost:8000/products"

# Example search: keyword + price range
curl "http://localhost:8000/products/search?q=Book&min_price=10&max_price=100"
```

You should see:

- `{"status": "UP"}` for `/health`.
- Seed categories and products for `/categories` and `/products`.
- A filtered result for `/products/search` containing the `Programming Book` product.

---

## Local Development (Optional)

The recommended way to run the service is via Docker Compose. However, you can also run it locally if you configure a local Postgres instance and set `DATABASE_URL` appropriately.

Example steps:

1. Create a local PostgreSQL database and user that match the credentials in `docker-compose.yml`.
2. Set an environment variable:

   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/product_catalog"
   ```

3. Install dependencies in a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   export PYTHONPATH=$PWD/src
   uvicorn app.main:app --reload
   ```

---

## API Documentation

FastAPI automatically exposes interactive documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

These pages are generated from the OpenAPI schema and allow you to explore and test the API from your browser.

---

## Testing

If you add tests (e.g., under `tests/`), you can run them using `pytest`:

```bash
pytest
```

This repository is structured to be test‑friendly due to the separation of concerns between API, services, and storage.

---

## Project Structure (Summary)

```text
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── schema.sql
└── src
    └── app
        ├── api
        │   ├── products.py
        │   └── categories.py
        ├── models.py
        ├── schemas.py
        ├── repositories
        │   ├── base.py
        │   ├── product_repository.py
        │   └── unit_of_work.py
        ├── main.py
        └── ...
```

---

## How to Submit (for Partnr Task)

1. Ensure all changes are committed and pushed to your Git repository.
2. Confirm the Docker setup works:

   ```bash
   docker-compose down
   docker-compose up --build
   ```

3. Verify the endpoints:

   ```bash
   curl "http://localhost:8000/health"
   curl "http://localhost:8000/categories"
   curl "http://localhost:8000/products"
   curl "http://localhost:8000/products/search?q=Book&min_price=10&max_price=100"
   ```
