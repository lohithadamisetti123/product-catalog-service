FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./scripts ./scripts
COPY ./schema.sql ./schema.sql

ENV PYTHONPATH=/app/src

CMD ["sh", "-c", "python -m scripts.seed_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
