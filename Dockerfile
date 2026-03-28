# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# Copy poetry files first for caching
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY app /app/app
COPY tests /app/tests

# Set PYTHONPATH for imports
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start FastAPI
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
