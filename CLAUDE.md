# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Loops API is a FastAPI backend for a Korean vocabulary learning application using FSRS (Free Spaced Repetition Scheduler) algorithm. It uses SQLModel (SQLAlchemy + Pydantic) for async database operations with PostgreSQL, Supabase for authentication, and `uv` for package management.

## Common Commands

This project uses [just](https://just.systems) as a command runner. Install with `brew install just` (macOS).

```bash
# Development
just dev                    # Start dev server (port 8080)
just setup                  # Initial setup (install deps, create .env)
just install                # Install dependencies (uv sync)

# Database Migrations
just migrate                # Apply migrations
just revision "message"     # Create new migration (requires confirmation)
just rollback               # Rollback last migration
just current                # Show current revision
just history                # View migration history
just check-migrations       # Check for pending migrations

# Database
just db-seed                # Seed with sample data
just db-test                # Test database connection
just reset                  # Reset database (⚠️ destructive)

# Docker
just docker-up              # Start containers
just docker-down            # Stop containers
just docker-logs            # View logs
just docker-migrate         # Apply migrations in Docker

# Utilities
just info                   # Show environment info
just health                 # Check API health (requires running server)
just clean                  # Clean Python cache
```

**Raw commands** (without just):

```bash
uv run python src/main.py                           # Start server
uv run alembic upgrade head                         # Apply migrations
uv run alembic revision --autogenerate -m "msg"     # Create migration
```

## Architecture

### Directory Structure

```text
src/
├── app/
│   ├── main.py              # FastAPI app, middleware, exception handlers
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Async session factory, engine
│   ├── api/                  # Route handlers (domain-based)
│   │   ├── routes.py         # Router aggregator
│   │   ├── auth.py           # Authentication (Supabase)
│   │   ├── profiles.py       # User profiles
│   │   ├── cards.py          # Vocabulary cards
│   │   ├── decks.py          # Deck management
│   │   ├── progress.py       # FSRS learning progress
│   │   ├── study.py          # Study sessions
│   │   ├── stats.py          # Statistics
│   │   └── quiz.py           # Quiz functionality
│   ├── core/
│   │   ├── security.py       # Supabase client, token verification
│   │   ├── dependencies.py   # FastAPI dependencies (CurrentActiveProfile)
│   │   ├── exceptions.py     # Custom exception classes
│   │   └── logging.py        # Structured logging (loguru)
│   ├── models/
│   │   ├── base.py           # TimestampMixin
│   │   ├── enums.py          # CardState enum
│   │   ├── tables/           # SQLModel table definitions
│   │   └── schemas/          # Pydantic DTOs
│   └── services/             # Business logic (static methods)
├── alembic/                  # Database migrations
└── scripts/                  # Utility scripts (seed_data.py)
```

### Model Architecture

Models are split into two directories:

1. **Tables** (`src/app/models/tables/`): Database models with `table=True`
   - `Profile` - User profile linked to Supabase Auth (UUID primary key)
   - `VocabularyCard` - Korean vocabulary with cloze sentences, examples
   - `UserCardProgress` - FSRS learning state per user-card
   - `Deck` - Word collections
   - `Favorite` - User favorites
   - `UserSelectedDeck` - User's selected decks for study

2. **Schemas** (`src/app/models/schemas/`): Pydantic models for API DTOs
   - `*Create`, `*Read`, `*Update` patterns
   - Request/Response models for each domain

**Pattern for new models**:

```python
# src/app/models/tables/entity.py
class EntityBase(SQLModel):
    name: str

class Entity(EntityBase, TimestampMixin, table=True):
    __tablename__ = "entities"
    id: int = Field(default=None, primary_key=True)

# src/app/models/schemas/entity.py
class EntityCreate(EntityBase): pass
class EntityRead(EntityBase):
    id: int
    created_at: datetime
```

**Critical**: Import new models in both `src/app/models/tables/__init__.py` AND `src/app/models/__init__.py` for Alembic detection.

### Authentication

Uses **Supabase Auth** (not local JWT):

- `Profile.id` is the Supabase `auth.users.id` UUID
- Token verification via `get_supabase_client()` in `src/app/core/security.py`
- Protected routes use `CurrentActiveProfile` dependency from `src/app/core/dependencies.py`

```python
from app.core.dependencies import CurrentActiveProfile

@router.get("/protected")
async def protected_route(profile: CurrentActiveProfile):
    return {"user_id": profile.id}
```

### Service Layer

Business logic in `src/app/services/` using static methods:

```python
class EntityService:
    @staticmethod
    async def get_entity(session: AsyncSession, entity_id: int) -> Entity | None:
        return await session.get(Entity, entity_id)
```

### FSRS Integration

Uses `py-fsrs` library for spaced repetition:

- `UserCardProgress` stores FSRS state (stability, difficulty, scheduled_days, lapses, card_state)
- `CardState` enum: NEW, LEARNING, REVIEW, RELEARNING
- Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
- See `src/app/services/user_card_progress_service.py` for integration

### API Routes

All routes mounted at `/api/v1` (configurable via `API_V1_PREFIX`):

| Prefix | File | Description |
|--------|------|-------------|
| `/auth` | `auth.py` | Register, login, refresh, logout, me |
| `/profiles` | `profiles.py` | Profile CRUD, settings |
| `/cards` | `cards.py` | Vocabulary cards |
| `/decks` | `decks.py` | Deck management |
| `/progress` | `progress.py` | FSRS review, due cards |
| `/study` | `study.py` | Study sessions |
| `/stats` | `stats.py` | Learning statistics |
| `/quiz` | `quiz.py` | Quiz functionality |

## Development Patterns

### Adding a New Entity

1. Create table model in `src/app/models/tables/`
2. Create schemas in `src/app/models/schemas/`
3. Export in `src/app/models/tables/__init__.py`
4. Export in `src/app/models/schemas/__init__.py`
5. Export in `src/app/models/__init__.py`
6. Create service in `src/app/services/`
7. Create router in `src/app/api/` and register in `routes.py`
8. Generate migration: `just revision "add entity"`
9. Apply migration: `just migrate`

### Error Handling

Custom exceptions in `src/app/core/exceptions.py`:

- `NotFoundError` (404)
- `ValidationError` (400)
- `AuthenticationError` (401)
- `AuthorizationError` (403)
- `ConflictError` (409)
- `DatabaseError` (500)

```python
from app.core.exceptions import NotFoundError

if not entity:
    raise NotFoundError(f"Entity {id} not found", resource="entity")
```

### Database Queries

```python
from sqlmodel import select

# Single result
result = await session.execute(select(Entity).where(Entity.id == id))
entity = result.scalar_one_or_none()

# Multiple results
result = await session.execute(select(Entity).offset(skip).limit(limit))
entities = list(result.scalars().all())
```

## Environment Configuration

Required in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/loops

# Supabase Auth
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Application
DEBUG=True
ALLOWED_ORIGINS=*
API_V1_PREFIX=/api/v1
```

## Troubleshooting

**Migration not detecting changes**: Ensure model is imported in `src/app/models/__init__.py`

**Database connection error**: Run `just docker-up` or ensure PostgreSQL is running

**Auth token invalid**: Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

## Quick Reference

```bash
# Full development cycle
just setup                  # First time setup
just docker-up              # Start database
just migrate                # Apply migrations
just db-seed                # (Optional) Add sample data
just dev                    # Start server

# After model changes
just revision "description" # Create migration
just migrate                # Apply migration
just current                # Verify
```
