# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI application using SQLModel (SQLAlchemy + Pydantic) for async database operations with PostgreSQL/Supabase. The project uses `uv` for package management and Alembic for database migrations.

## Common Commands

### Running the Application

```bash
# Development mode with auto-reload
uv run python main.py

# Docker Compose (includes PostgreSQL)
docker-compose up --build

# Run migrations inside Docker
docker-compose exec api uv run alembic upgrade head
```

### Database Migrations

```bash
# Create a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Dependencies

```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Sync dependencies
uv sync
```

## Architecture

### Database Session Management

The application uses a dependency injection pattern for database sessions:

- **Session Factory**: `async_session_maker` in `app/database.py` creates async SQLModel sessions
- **Dependency**: `get_session()` in `app/database.py` provides sessions to route handlers
- **Session Lifecycle**: Sessions auto-commit on success and rollback on exception
- **Usage**: Inject with `session: AsyncSession = Depends(get_session)` in route handlers

### Model Architecture

The project follows a layered schema pattern with SQLModel:

1. **Base Models** (`app/models/base.py`): Shared mixins like `TimestampMixin` for `created_at`/`updated_at`
2. **Database Models** (e.g., `User` in `app/models/user.py`): Table models with `table=True`
3. **Schema Models**: Separate Pydantic models for different operations:
   - `*Create`: For POST requests (excludes id, timestamps)
   - `*Read`: For responses (includes id, computed fields)
   - `*Update`: For PATCH requests (all fields optional)
   - `*Base`: Shared fields between schemas

**Important**: Database models inherit from both their Base schema and mixins, e.g., `User(UserBase, TimestampMixin, table=True)`

### Service Layer Pattern

Business logic is organized in service classes under `app/services/`:

- Services use static methods (no instance state)
- Each service corresponds to a domain entity (e.g., `UserService`)
- Services handle CRUD operations and business rules
- Routes call services and handle HTTP concerns (validation, status codes, exceptions)

**Pattern**:

```python
class EntityService:
    @staticmethod
    async def create_entity(session: AsyncSession, data: EntityCreate) -> Entity:
        entity = Entity(**data.model_dump())
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity
```

### Routing Structure

- **Main App**: `app/main.py` - FastAPI app setup with CORS, lifespan management
- **API Router**: `app/api/routes.py` - All v1 routes registered here
- **Route Prefix**: Routes are mounted at `/api/v1` (configurable via `API_V1_PREFIX`)
- **Built-in Endpoints**: `/` (root), `/health` (health check)

### Configuration Management

Configuration uses `pydantic-settings` with environment variable support:

- **Config Class**: `Settings` in `app/config.py`
- **Singleton**: `settings` instance auto-loads from `.env`
- **Case Insensitive**: Environment variables are case-insensitive
- **Validation**: Pydantic validates types and provides defaults

### Alembic Integration

Alembic is configured to work with SQLModel's async engine:

- **Environment**: `alembic/env.py` imports all models and uses async migrations
- **Metadata**: Uses `SQLModel.metadata` for autogenerate
- **Database URL**: Automatically pulled from `app.config.settings.database_url`
- **Model Registration**: Import all models in `alembic/env.py` AND `app/models/__init__.py`

**Critical**: When adding new models, import them in `app/models/__init__.py` so Alembic detects them.

## Development Patterns

### Adding a New Model/Entity

1. Create model file in `app/models/` with Base, table, Create, Read, Update schemas
2. Import model in `app/models/__init__.py`
3. Create service in `app/services/` with CRUD operations
4. Add routes in `app/api/routes.py` using the service
5. Generate migration: `uv run alembic revision --autogenerate -m "add entity"`
6. Review and apply migration: `uv run alembic upgrade head`

### Database Queries

Use SQLModel's `select()` for queries:

```python
from sqlmodel import select

# Single result
statement = select(User).where(User.id == user_id)
result = await session.execute(statement)
user = result.scalar_one_or_none()

# Multiple results
statement = select(User).offset(skip).limit(limit)
result = await session.execute(statement)
users = list(result.scalars().all())
```

### Authentication & Security

The application implements full JWT-based authentication with bcrypt password hashing:

**Security Module** (`app/core/security.py`):

- `verify_password()`: Validates plain password against bcrypt hash
- `get_password_hash()`: Creates bcrypt hash from plain password
- `create_access_token()`: Generates JWT token with configurable expiration
- Uses `passlib[bcrypt]` for password hashing and `python-jose[cryptography]` for JWT

**Dependencies Module** (`app/core/dependencies.py`):

- `oauth2_scheme`: OAuth2PasswordBearer with token URL `/api/v1/auth/login`
- `get_current_user()`: Dependency that validates JWT and returns authenticated User
- Decodes JWT, verifies user exists, raises 401 if invalid

**Authentication Flow**:

1. **Registration** (`POST /api/v1/auth/register`): Creates user with hashed password
2. **Login** (`POST /api/v1/auth/login`): Validates credentials, returns JWT access token
3. **Protected Routes**: Use `Depends(get_current_user)` to require authentication
4. **Current User** (`GET /api/v1/auth/me`): Returns authenticated user info

**Important Security Rules**:

- Never return `password` or `hashed_password` in response schemas
- `UserRead` schema excludes password fields
- Always hash passwords in `UserService.create_user()` and `UserService.update_user()`
- JWT secrets should be changed in production (configured in `.env`)

### FSRS Integration

The application uses the `py-fsrs` library (v6.3.0) for spaced repetition algorithm:

**Integration Pattern** (`app/services/user_card_progress_service.py`):

```python
from fsrs import FSRS, Card, Rating

# Convert DB model to FSRS Card
@staticmethod
def progress_to_card(progress: UserCardProgress) -> Card:
    return Card(
        due=progress.next_review_date,
        stability=progress.stability or 0.0,
        difficulty=progress.difficulty or 5.0,
        elapsed_days=progress.elapsed_days,
        scheduled_days=progress.scheduled_days,
        reps=progress.repetitions,
        lapses=progress.lapses,
        state=State.New if progress.card_state == CardState.NEW else ...,
        last_review=progress.last_review_date,
    )

# Process review with FSRS
@staticmethod
async def process_review(session, user_id, card_id, rating):
    fsrs = FSRS()
    card = progress_to_card(progress)
    scheduling_cards = fsrs.repeat(card, now)
    updated_card = scheduling_cards[rating].card
    # Update progress with FSRS results
```

**FSRS Fields in UserCardProgress**:

- `stability`: Memory stability (FSRS core parameter)
- `difficulty`: Card difficulty 1-10 (FSRS core parameter)
- `scheduled_days`: Scheduled interval from FSRS
- `lapses`: Number of times forgotten
- `reps_since_lapse`: Successful reviews since last lapse
- `elapsed_days`: Days between reviews
- `card_state`: NEW/LEARNING/REVIEW/RELEARNING (maps to FSRS State)

**Rating System**:

- 1 = Again (forgot)
- 2 = Hard (difficult)
- 3 = Good (remembered)
- 4 = Easy (very easy)

**API Endpoint**: `POST /api/v1/progress/review` with `ReviewRequest` body

## Environment Configuration

Required environment variables in `.env`:

**Database Configuration**:

- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql+asyncpg://user:pass@host:port/db`)
- `DATABASE_ECHO`: SQL query logging (default: False)

**Security Configuration**:

- `SECRET_KEY`: JWT signing secret key (**MUST change in production**)
- `ALGORITHM`: JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

**Application Configuration**:

- `APP_NAME`: Application name (default: "Loops API")
- `APP_VERSION`: API version (default: "0.1.0")
- `DEBUG`: Enable auto-reload and debug mode (default: False)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: "\*")
- `API_V1_PREFIX`: API route prefix (default: "/api/v1")

**Example `.env` file**:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/loops
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
ALLOWED_ORIGINS=*
```

## Data Models Reference

The application has 8 core models with comprehensive schemas:

### 1. User (`app/models/user.py`)

**Purpose**: User account and profile management

**Key Fields**:

- `id`: Integer primary key
- `username`: Unique username (max 50 chars)
- `email`: Unique email with validation
- `hashed_password`: Bcrypt hashed password (never exposed in Read schema)
- `subscription_type`: FREE/PREMIUM/ENTERPRISE (enum)
- `total_cards_learned`, `total_study_time_minutes`: Learning statistics
- `current_streak`, `longest_streak`: Streak tracking
- `last_study_date`: Date type for streak calculations

**Subscription Types**:

```python
class SubscriptionType(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
```

**Schemas**: `UserBase`, `User`, `UserCreate`, `UserRead`, `UserUpdate`, `UserLogin`

### 2. VocabularyCard (`app/models/vocabulary_card.py`)

**Purpose**: Korean vocabulary card content with rich metadata

**Key Fields**:

- `korean_word`: Korean text (max 100 chars, indexed)
- `pronunciation`: Korean pronunciation guide
- `meaning`: Primary meaning/translation
- `definition_en`: English definition
- `difficulty_level`: Integer 1-10
- `cefr_level`: A1/A2/B1/B2/C1/C2
- `usage_notes`, `etymology`: Text fields for additional context
- `is_verified`: Boolean verification flag
- `deck_id`: Foreign key to Deck (optional)

**JSONB Fields** (stored as JSON arrays):

- `example_sentences`: List of example sentences
- `synonyms`: List of synonyms
- `antonyms`: List of antonyms
- `related_words`: List of related vocabulary
- `collocations`: List of common word combinations

**Schemas**: `VocabularyCardBase`, `VocabularyCard`, `VocabularyCardCreate`, `VocabularyCardRead`, `VocabularyCardUpdate`

### 3. UserCardProgress (`app/models/user_card_progress.py`)

**Purpose**: Track FSRS-based learning progress for each user-card pair

**FSRS Core Fields**:

- `stability`: Memory stability (float)
- `difficulty`: Card difficulty 1-10 (float)
- `interval`: Days until next review (int)
- `scheduled_days`: FSRS scheduled interval (int)
- `lapses`: Times forgotten (int)
- `reps_since_lapse`: Reviews since last lapse (int)
- `card_state`: NEW/LEARNING/REVIEW/RELEARNING (enum)

**Statistics Fields**:

- `total_reviews`, `correct_count`, `wrong_count`: Review counts
- `accuracy_rate`: Success percentage (float)
- `average_response_time`: Response time in seconds (int)

**Timing Fields**:

- `next_review_date`: When to review next (datetime, indexed)
- `last_review_date`: Last review timestamp (datetime)
- `first_studied_at`: First study timestamp (datetime)
- `mastered_at`: Mastery achievement timestamp (datetime)

**JSONB Fields**:

- `quality_history`: Array of review history objects with date, quality, interval, stability, difficulty

**Unique Constraint**: `(user_id, card_id)` - one progress record per user-card pair

**Schemas**: `UserCardProgressBase`, `UserCardProgress`, `UserCardProgressCreate`, `UserCardProgressRead`, `UserCardProgressUpdate`, `ReviewRequest`, `ReviewResponse`

### 4. SyncQueue (`app/models/sync_queue.py`)

**Purpose**: Offline sync queue for managing data synchronization

**Key Fields**:

- `user_id`, `entity_type`, `entity_id`: Identify what to sync (all indexed)
- `operation`: CREATE/UPDATE/DELETE (enum)
- `payload`: JSONB flexible data payload
- `is_synced`: Boolean sync status (indexed)
- `retry_count`, `max_retries`: Retry management (default 3 retries)
- `priority`: Higher number = higher priority (int, default 0)
- `error_message`: Last error details (optional text)

**Timestamps**:

- `created_at`: When queued (datetime)
- `synced_at`: When synced (optional datetime)
- `last_retry_at`: Last retry timestamp (optional datetime)

**Schemas**: `SyncQueueBase`, `SyncQueue`, `SyncQueueCreate`, `SyncQueueRead`, `SyncQueueUpdate`

### 5. Deck (`app/models/deck.py`)

**Purpose**: Word collection/deck management

**Key Fields**:

- `name`: Deck name (max 200 chars)
- `description`: Deck description (optional text)
- `creator_id`: Foreign key to User (optional)
- `is_public`: Sharing visibility (boolean)
- `card_count`: Total cards in deck (int)
- `learning_count`: Cards being learned (int)

**Schemas**: `DeckBase`, `Deck`, `DeckCreate`, `DeckRead`, `DeckUpdate`

### 6. UserDeck (`app/models/user_deck.py`)

**Purpose**: User's relationship with decks and progress tracking

**Key Fields**:

- `user_id`, `deck_id`: Foreign keys (unique constraint together)
- `is_active`: Active study status (boolean)
- `cards_new`, `cards_learning`, `cards_review`: Card state counts
- `progress_percentage`: Overall progress 0-100 (float)
- `last_studied_at`: Last study timestamp (optional datetime)

**Schemas**: `UserDeckBase`, `UserDeck`, `UserDeckCreate`, `UserDeckRead`, `UserDeckUpdate`

### 7. StudySession (`app/models/study_session.py`)

**Purpose**: Track individual study sessions with detailed statistics

**Key Fields**:

- `user_id`, `deck_id`: Foreign keys (deck_id optional)
- `duration_minutes`: Session length (int)
- `cards_studied`: Number of cards reviewed (int)
- `accuracy_rate`: Session accuracy 0-100 (float)
- `device_type`: Device used (optional max 50 chars)
- `session_date`: When session occurred (datetime, indexed)

**Schemas**: `StudySessionBase`, `StudySession`, `StudySessionCreate`, `StudySessionRead`, `StudySessionUpdate`

### 8. AIInteraction (`app/models/ai_interaction.py`)

**Purpose**: Log AI interactions for analytics and improvement

**Key Fields**:

- `user_id`: Foreign key to User
- `interaction_type`: Type of AI interaction (max 50 chars)
- `model_used`: AI model identifier (max 100 chars)
- `user_input`: User's input text (optional)
- `ai_response`: AI's response text (optional)
- `tokens_used`: Token consumption (optional int)
- `response_time_ms`: Response latency (optional int)
- `feedback_rating`: User feedback 1-5 (optional int)
- `interaction_timestamp`: When interaction occurred (datetime)

**Schemas**: `AIInteractionBase`, `AIInteraction`, `AIInteractionCreate`, `AIInteractionRead`, `AIInteractionUpdate`

## Working with Enums

The application uses SQLModel's enum integration with proper database mapping:

**Defining Enums**:

```python
import enum
from sqlmodel import Column, Enum

class CardState(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    RELEARNING = "relearning"

class EntityBase(SQLModel):
    # Use enum directly in base schema
    status: CardState

class Entity(EntityBase, table=True):
    # Map to database with sa_column
    status: CardState = Field(
        sa_column=Column(Enum(CardState), nullable=False, index=True)
    )
```

**Current Enums**:

- `SubscriptionType`: FREE, PREMIUM, ENTERPRISE
- `CardState`: NEW, LEARNING, REVIEW, RELEARNING
- `OperationType`: CREATE, UPDATE, DELETE

## Working with JSONB Fields

PostgreSQL JSONB fields are used for flexible, structured data:

**Defining JSONB Fields**:

```python
from typing import Any
from sqlmodel import Column, JSON, Field

class Entity(SQLModel, table=True):
    # Array of objects
    history: Optional[dict[str, Any] | list[Any]] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    # Simple array
    tags: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON)
    )
```

**Current JSONB Fields**:

- `VocabularyCard.example_sentences`: List of sentence objects
- `VocabularyCard.synonyms/antonyms/related_words/collocations`: String arrays
- `UserCardProgress.quality_history`: Array of review objects
- `SyncQueue.payload`: Flexible operation data

**Querying JSONB** (when needed):

```python
from sqlalchemy import func

# JSON contains check
statement = select(Card).where(
    func.jsonb_path_exists(Card.tags, '$ ? (@ == "beginner")')
)
```

## Troubleshooting

### Common Issues and Solutions

**1. Database Connection Error**

```
OSError: Connect call failed
```

**Solution**: Ensure PostgreSQL is running:

```bash
docker-compose up -d db  # Start just the database
# or
pg_ctl start  # If using local PostgreSQL
```

**2. Migration Autogenerate Not Detecting Changes**

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected NULL
```

**Solution**: Ensure model is imported in `app/models/__init__.py`:

```python
from app.models.new_model import NewModel, NewModelCreate, NewModelRead, NewModelUpdate

__all__ = [
    ...,
    "NewModel",
    "NewModelCreate",
    "NewModelRead",
    "NewModelUpdate",
]
```

**3. JWT Token Invalid/Expired**

```
HTTPException: Could not validate credentials
```

**Solution**:

- Check `SECRET_KEY` matches between registration and login
- Verify token hasn't expired (check `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Ensure token is passed in `Authorization: Bearer <token>` header

**4. JSONB Field Type Errors**

```
TypeError: Object of type X is not JSON serializable
```

**Solution**: Use proper type hints and ensure data is JSON-serializable:

```python
# Correct
tags: Optional[list[str]] = ["tag1", "tag2"]

# Incorrect
tags: Optional[list[str]] = set(["tag1", "tag2"])  # Sets not JSON serializable
```

**5. Unique Constraint Violation**

```
IntegrityError: duplicate key value violates unique constraint
```

**Solution**: Check for existing records before creating:

```python
# Check if exists
existing = await session.execute(
    select(Entity).where(Entity.field == value)
)
if existing.scalar_one_or_none():
    raise HTTPException(status_code=400, detail="Already exists")
```

**6. Password Hashing Errors**

```
ValueError: Invalid salt
```

**Solution**: Ensure using the security module functions:

```python
from app.core.security import get_password_hash, verify_password

# Correct
hashed = get_password_hash(plain_password)

# Incorrect
hashed = bcrypt.hash(plain_password)  # Don't use bcrypt directly
```

## API Endpoint Patterns

All API routes are organized in `app/api/routes.py` and mounted at `/api/v1`. Authentication is required for all endpoints except registration and login.

### Current Endpoints (26 total)

**Authentication** (`app/api/auth.py`):

- `POST /api/v1/auth/register`: Register new user (no auth required)
- `POST /api/v1/auth/login`: Login and get JWT token (no auth required)
- `GET /api/v1/auth/me`: Get current user info (auth required)

**Users**:

- `POST /api/v1/users`: Create user (admin endpoint)
- `GET /api/v1/users`: List users with pagination
- `GET /api/v1/users/{user_id}`: Get specific user
- `PATCH /api/v1/users/{user_id}`: Update user
- `DELETE /api/v1/users/{user_id}`: Delete user

**Vocabulary Cards**:

- `POST /api/v1/cards`: Create card
- `GET /api/v1/cards`: List cards with optional filters (difficulty_level, deck_id)
- `GET /api/v1/cards/search?q={term}`: Search cards by korean_word/meaning
- `GET /api/v1/cards/{card_id}`: Get specific card
- `PATCH /api/v1/cards/{card_id}`: Update card
- `DELETE /api/v1/cards/{card_id}`: Delete card

**User Card Progress (FSRS)**:

- `POST /api/v1/progress`: Create progress record
- `POST /api/v1/progress/review`: Submit review with rating (1-4)
- `GET /api/v1/progress/user/{user_id}`: Get user's progress records
- `GET /api/v1/progress/user/{user_id}/due`: Get due cards for review
- `GET /api/v1/progress/{progress_id}`: Get specific progress
- `PATCH /api/v1/progress/{progress_id}`: Update progress
- `DELETE /api/v1/progress/{progress_id}`: Delete progress

**Sync Queue**:

- `POST /api/v1/sync`: Create sync queue entry
- `GET /api/v1/sync/user/{user_id}/pending`: Get pending sync items
- `PATCH /api/v1/sync/{queue_id}/synced`: Mark as synced
- `DELETE /api/v1/sync/{queue_id}`: Delete queue entry

### Adding New Endpoints

When adding new endpoints, follow this pattern:

1. **Define route handler in `app/api/routes.py`**:

```python
@router.post("/entities", response_model=EntityRead)
async def create_entity(
    entity_data: EntityCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntityRead:
    """Create a new entity."""
    entity = await EntityService.create_entity(session, entity_data)
    return entity
```

2. **Implement service method in `app/services/entity_service.py`**:

```python
@staticmethod
async def create_entity(session: AsyncSession, data: EntityCreate) -> Entity:
    entity = Entity(**data.model_dump())
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
```

3. **Use Depends() for dependency injection**:

- `Depends(get_current_user)`: Requires authentication, provides User object
- `Depends(get_session)`: Provides database session
- Use `Annotated[Type, Depends(dep)]` for type safety

### Testing Endpoints

**Using curl**:

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123" | jq -r .access_token)

# Use authenticated endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Submit card review
curl -X POST http://localhost:8000/api/v1/progress/review \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"card_id":1,"rating":3}'
```

**Using Python**:

```python
import requests

# Register and login
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})

response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "testuser",
    "password": "password123"
})
token = response.json()["access_token"]

# Use authenticated endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
user = response.json()

# Submit card review
response = requests.post(
    "http://localhost:8000/api/v1/progress/review",
    headers=headers,
    json={"card_id": 1, "rating": 3}
)
review_result = response.json()
```

## Best Practices for AI Collaboration

### Code Consistency

1. **Always follow the Base/Table/Create/Read/Update pattern** for models
2. **Use static methods in services** - no instance state
3. **Use dependency injection** for session and auth
4. **Import models in `__init__.py`** for Alembic detection
5. **Use type hints** with `Annotated` for FastAPI dependencies

### Security Checklist

- [ ] Never expose `password` or `hashed_password` in Read schemas
- [ ] Always use `get_password_hash()` for password hashing
- [ ] Use `Depends(get_current_user)` for protected routes
- [ ] Change `SECRET_KEY` in production
- [ ] Validate user input with Pydantic models
- [ ] Use HTTPS in production

### Database Best Practices

- [ ] Use indexes on frequently queried fields (id, foreign keys, status fields)
- [ ] Add unique constraints where appropriate
- [ ] Use CASCADE for foreign key deletions where appropriate
- [ ] Review migrations before applying (`uv run alembic upgrade head`)
- [ ] Use `scalar_one_or_none()` for single results (returns None if not found)
- [ ] Use `scalars().all()` for multiple results

### FSRS Integration Checklist

- [ ] Always use `progress_to_card()` to convert DB model to FSRS Card
- [ ] Use `fsrs.repeat(card, now)` to get scheduling options
- [ ] Access updated card via `scheduling_cards[rating].card`
- [ ] Update all FSRS fields: stability, difficulty, scheduled_days, lapses, card_state
- [ ] Append to quality_history for tracking
- [ ] Rating must be 1-4 (validated by Pydantic)

## Docker Notes

- **Multi-stage Build**: Uses UV's official Docker image for dependency installation
- **Non-root User**: Runtime uses `app` user (UID 1000)
- **Volume Mounts**: `docker-compose.yaml` mounts `./app` and `main.py` for hot reload
- **Database**: docker-compose includes PostgreSQL 16 with persistent volume
- **Health Checks**: Both API and PostgreSQL have health checks configured

## Quick Reference Commands

```bash
# Start development server
uv run python main.py

# Start with Docker
docker-compose up --build

# Generate migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Seed database
uv run python src/scripts/seed_data.py

# Add dependency
uv add package-name

# Run in background with logs
docker-compose up -d && docker-compose logs -f api
```
