# Authentication and User Management

The Habit Tracker application uses **JSON Web Tokens (JWT)** for secure, stateless authentication. This document explains the theoretical background and the specific implementation details within the project.

## JWT Theory

JSON Web Tokens (JWT) are an open standard (RFC 7519) that defines a compact and self-contained way for securely transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed.

### Structure

A JWT consists of three parts separated by dots (`.`):

1.  **Header**: Indicates the token type (JWT) and the signing algorithm (e.g., HS256).
2.  **Payload**: Contains the claims. Claims are statements about an entity (typically, the user) and additional data.
    *   **Registered claims**: Predefined claims like `sub` (subject), `exp` (expiration time), `iat` (issued at).
    *   **Public/Private claims**: Custom custom data defined by the application.
3.  **Signature**: Used to verify that the message wasn't changed along the way. It is created by taking the encoded header, the encoded payload, a secret, and the algorithm specified in the header.

### Why Stateless?

We use JWTs for **stateless authentication**. This means the server does not need to keep a session record (e.g., in a database or memory) for each logged-in user.
*   The user logs in once and receives a token.
*   The token itself contains all necessary information (like the User ID).
*   The server verifies the token's signature on each request to ensure it's valid and hasn't expired.

## User Management

The application provides endpoints for users to sign up and log in.

### Registration

*   **Endpoint**: `POST /auth/register`
*   **Input**: Email and password.
*   **Process**:
    1.  Checks if the email is already registered.
    2.  Hashes the password using **bcrypt** (via `passlib`). We never store plain-text passwords.
    3.  Creates a new `User` entity and persists it using the `UserRepository`.
*   **Output**: The created user object (excluding the password).

### Login

*   **Endpoint**: `POST /auth/login`
*   **Input**: Email and password.
*   **Process**:
    1.  Retrieves the user by email.
    2.  Verifies the provided password against the stored hash.
    3.  If valid, generates a JWT access token containing the user's ID in the `sub` claim.
*   **Output**: JSON object containing the `access_token` and `token_type` ("bearer").

## Code Integration

The authentication system is integrated across several layers of the application:

### 1. Security Module (`habit_tracker.application.security`)

This module contains the low-level cryptographic primitives:
*   `hash_password(password: str) -> str`: Hashes a plain password.
*   `verify_password(password: str, hashed: str) -> bool`: Verifies a password against a hash.
*   `create_access_token(data: dict) -> str`: Encodes a dictionary of claims into a JWT string.
*   `decode_access_token(token: str) -> dict`: Decodes and validates a JWT string.

### 2. Application Services (`habit_tracker.application.services`)

*   **`UserRegistrationService`**: Orchestrates the registration flow. It ensures domain invariants (like unique emails) are respected.
*   **`AuthenticationService`**: Handles the logic of checking credentials. It returns the `User` object if authentication succeeds, or raises an error.

### 3. API Layer (`habit_tracker.interfaces.api.app`)

We use **FastAPI's security utilities** to integrate authentication into the HTTP layer:

*   **`oauth2_scheme`**: Defines that the API uses OAuth2 with Password flow, pointing to `/auth/login` for token retrieval.
*   **`get_current_user` Dependency**: This function is used in route signatures to protect endpoints.
    1.  It extracts the token from the `Authorization` header.
    2.  Decodes the token to get the user ID (`sub`).
    3.  Loads the user from the `UserRepository`.
    4.  Checks if the user is active.
    5.  Returns the `User` object or raises `401 Unauthorized`.

### 4. Repositories

The `UserRepository` interface (Protocol) defines the contract for user persistence. We currently have:
*   `InMemoryUserRepository`: For testing and local development.
*   `SQLiteUserRepository`: For persistent storage.

## Protected Endpoints

All habit-related endpoints require authentication. The `get_current_user` dependency is injected into route handlers to enforce this:

### Authenticated Endpoints

*   `POST /habits` - Create a new habit (requires authentication)
*   `GET /habits` - List user's habits (requires authentication, filtered by user)
*   `POST /habits/{id}/complete` - Complete a habit (requires authentication and ownership)
*   `GET /habits/{id}/streak` - Get habit streak (requires authentication and ownership)

### Current User Endpoint

*   **Endpoint**: `GET /me`
*   **Purpose**: Returns the currently authenticated user's information
*   **Authentication**: Required (uses `get_current_user` dependency)
*   **Output**: User object with `id`, `email`, `is_active`, and `created_at`

## Multi-Tenancy and User Isolation

The application implements strict **multi-tenant isolation** to ensure users can only access their own data.

### User-Habit Relationship

*   Each `Habit` entity has a `user_id` field that links it to its owner
*   The `user_id` is automatically set when creating a habit using the authenticated user's ID
*   The `HabitCreated` domain event does **not** include `user_id` (kept minimal for event design)

### Repository Methods

The `HabitRepository` provides methods for user-scoped queries:

*   `list_by_user_id(user_id: UUID) -> List[Habit]`: Returns all habits for a specific user
*   `get_by_user_id(user_id: UUID) -> Habit | None`: Returns the first habit for a user (utility method)

### Service Layer Authorization

The `HabitTrackerService` enforces ownership checks:

*   **`list_habits_for_user(user_id: UUID)`**: Returns only habits belonging to the specified user
*   **`complete_habit(habit_id: UUID, user_id: UUID)`**: Verifies the habit belongs to the user before allowing completion
    *   Raises `PermissionError` if the habit belongs to a different user
*   **`calculate_streak(habit_id: UUID, user_id: UUID, rule: StreakRule | None)`**: Verifies ownership before calculating streaks
    *   Raises `PermissionError` if the habit belongs to a different user

### API Layer Security

The API layer converts permission errors to 404 responses to avoid information leakage:

```python
try:
    completion = service.complete_habit(habit_id, user_id=current_user.id)
except KeyError:
    raise HTTPException(status_code=404, detail="Habit not found")
except PermissionError:
    # Return 404 instead of 403 to avoid leaking habit existence
    raise HTTPException(status_code=404, detail="Habit not found")
```

**Security Rationale**: Returning 404 (instead of 403) prevents attackers from discovering which habit IDs exist in the system by attempting to access them with different user accounts.

### Database Schema

The SQLite schema enforces referential integrity:

```sql
CREATE TABLE habits (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    schedule TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

*   The `user_id` foreign key ensures habits are always linked to valid users
*   `ON DELETE CASCADE` ensures that when a user is deleted, all their habits are automatically removed

## Testing Multi-Tenancy

The test suite includes comprehensive multi-tenant tests (`tests/test_habits_multitenant.py`):

1.  **User Isolation Test**: Verifies that User A and User B each see only their own habits when calling `GET /habits`
2.  **Permission Test**: Verifies that User B cannot complete User A's habit (receives 404)
3.  **Ownership Test**: Verifies that users can only interact with their own habits

These tests ensure the application maintains strict data isolation between users.
