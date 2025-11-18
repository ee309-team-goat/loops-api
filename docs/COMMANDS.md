# Loops API - Quick Command Reference

> **Tools Used:** `justfile` for simple tasks, `cli.py` for complex operations

## Getting Started

```bash
just setup              # Complete project setup
just dev                # Start development server
just                    # Show all commands
```

## Daily Development Workflow

### Starting Work
```bash
just dev                # Start server with auto-reload
# or
just docker-up          # Start with Docker
```

### Making Database Changes
```bash
# 1. Modify your models in src/app/models/
# 2. Create migration
just revision "Add new field"

# 3. Review the migration in src/alembic/versions/
# 4. Apply migration
just migrate

# If something goes wrong
just rollback           # Undo last migration
```

### Working with Users
```bash
just user-create        # Interactive user creation
just user-list          # List all users
```

### Health Checks
```bash
just health             # Check if API is running
just db-test            # Test database connection
just check              # Run all health checks
```

## Database Commands

| Command | Description |
|---------|-------------|
| `just migrate` | Apply all pending migrations |
| `just rollback` | Rollback last migration |
| `just reset` | Reset database completely |
| `just history` | Show migration history |
| `just current` | Show current revision |

### Advanced Database Operations

```bash
# Create migration (Just)
just revision "Description of changes"

# Rollback multiple migrations (CLI only)
uv run python cli.py db:rollback -s 3

# Reset database without confirmation prompt (CLI only)
uv run python cli.py db:reset -y
```

## Docker Commands

| Command | Description |
|---------|-------------|
| `just docker-up` | Start containers (detached) |
| `just docker-down` | Stop containers |
| `just docker-logs` | View logs (follow mode) |

### Advanced Docker Operations

```bash
# Start with fresh build
uv run python cli.py docker:up -b -d

# Stop and remove volumes
uv run python cli.py docker:down -v

# View specific service logs
uv run python cli.py docker:logs -f api
uv run python cli.py docker:logs -f db

# Run migrations in Docker
docker-compose exec api uv run alembic upgrade head
```

## User Management

```bash
# Interactive mode
just user-create

# With arguments (Just)
just user-create "Jane Doe" "jane@example.com"

# With arguments (CLI)
uv run python cli.py user:create -n "Jane Doe" -e "jane@example.com"

# List users
just user-list
```

## Utilities

```bash
just clean              # Clean Python cache files
just                    # Show all Just commands
uv run python cli.py --help  # Show all CLI commands
```

## API Endpoints

Once the server is running (`just dev` or `just docker-up`):

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- Root: http://localhost:8000/

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
just db-test

# Check .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL

# For Supabase
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# For local PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops
```

### Migration Issues
```bash
# Check current state
just current
just history

# Reset if needed
just reset
```

### Docker Issues
```bash
# View logs
just docker-logs

# Restart containers
just docker-down
just docker-up

# Fresh start with rebuild (CLI)
uv run python cli.py docker:down -v
uv run python cli.py docker:up -b -d
```

## Common Workflows

### Adding a New Model
1. Create model in `src/app/models/new_model.py`
2. Import in `src/app/models/__init__.py`
3. Create migration: `just revision "Add new model"`
4. Review migration file in `src/alembic/versions/`
5. Apply: `just migrate`
6. Create service in `src/app/services/`
7. Add routes in `src/app/api/routes.py`

### Updating Dependencies
```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Sync dependencies
uv sync
```

### Production Deployment
```bash
# Set environment variables
DEBUG=False

# Run migrations
just migrate

# Start server (production mode)
uv run python src/main.py
```

## Environment Variables

Key variables in `.env`:

```env
# Application
APP_NAME=Loops API
APP_VERSION=0.1.0
DEBUG=True                  # Set to False in production

# API
API_V1_PREFIX=/api/v1

# CORS
ALLOWED_ORIGINS=*           # Restrict in production

# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://...
DATABASE_ECHO=False         # Set to True to see SQL queries
```

## Tips

- Use `just` commands for daily tasks (faster to type)
- Use `uv run python cli.py` for complex operations with special options
- Always review auto-generated migrations before applying
- Keep DATABASE_ECHO=False in production
- Use DEBUG=True only in development
- Run `just check` to verify setup (runs health + db-test)
- Type `just` to see all available commands
