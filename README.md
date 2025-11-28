# Habit Tracker API

A simple, clean, and efficient Habit Tracker API built with Python and FastAPI. This project allows users to create habits, track their completion, and calculate streaks.

## Features

- **Create Habits**: Define habits with specific schedules (e.g., daily, 3 times per week).
- **Track Completions**: Mark habits as completed for a given day.
- **Calculate Streaks**: Automatically calculate current streaks based on completion history.
- **In-Memory Storage**: Currently uses in-memory repositories for simplicity (data is lost on restart).

## Prerequisites

- **Python 3.11+**
- **Docker** (optional, for containerized execution)

## Getting Started

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd habit-tracker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    uvicorn habit_tracker.interfaces.api.app:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

5.  **Explore the API:**
    Open your browser and navigate to `http://127.0.0.1:8000/docs` to see the interactive Swagger UI documentation.

### Running with Docker

1.  **Build and run the container:**
    ```bash
    docker-compose up --build
    ```

2.  **Access the API:**
    The API will be running at `http://0.0.0.0:8000`.

## Running Tests

To run the test suite, make sure you have the development dependencies installed (included in `requirements.txt`).

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=habit_tracker
```

## Project Structure

- `habit_tracker/`: Main application source code.
    - `application/`: Application services and business logic.
    - `domain/`: Domain models and rules.
    - `infrastructure/`: Infrastructure implementations (repositories, clock).
    - `interfaces/`: API endpoints and entry points.
- `tests/`: Unit and integration tests.
