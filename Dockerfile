FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (minimal for now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (user-level is fine inside container)
RUN pip install --no-cache-dir poetry

# Copy only dependency files first (better caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies (including dev for now; can switch to --without dev for prod)
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the source code
COPY . .

EXPOSE 8000

# Run the app via Poetry
CMD ["poetry", "run", "uvicorn", "habit_tracker.interfaces.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
