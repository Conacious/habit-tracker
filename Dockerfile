FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "habit_tracker.interfaces.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
