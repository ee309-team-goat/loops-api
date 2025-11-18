# Loops API - Just Commands
# Install just: brew install just (or see https://just.systems)
# Run: just <command>

# Show all available commands
default:
    @just --list

# Complete project setup
setup:
    @echo "🔧 Setting up Loops API..."
    uv sync
    @if [ ! -f .env ]; then cp .env.example .env && echo "✓ Created .env"; fi
    @echo "⚠️  Update DATABASE_URL in .env, then run: just migrate"

# Start development server
dev:
    @echo "🚀 Starting development server..."
    uv run python src/main.py

# Run database migrations
migrate:
    @echo "📦 Running migrations..."
    uv run alembic upgrade head

# Rollback last migration
rollback:
    @echo "↩️  Rolling back migration..."
    uv run alembic downgrade -1

# Create new migration with autogenerate
[confirm("This will create a new migration. Continue?")]
revision MESSAGE:
    @echo "📝 Creating migration: {{MESSAGE}}"
    uv run alembic revision --autogenerate -m "{{MESSAGE}}"

# Show migration history
history:
    @echo "📜 Migration history:"
    uv run alembic history

# Show current revision
current:
    @echo "📍 Current revision:"
    uv run alembic current

# Reset database (requires confirmation)
[confirm("⚠️  This will reset the database. Continue?")]
reset:
    @echo "🔄 Resetting database..."
    uv run alembic downgrade base
    uv run alembic upgrade head

# Test database connection
db-test:
    @echo "🔌 Testing database connection..."
    uv run python cli.py db:test

# Check API health
health:
    @echo "🏥 Checking API health..."
    uv run python cli.py health

# Create a new user (interactive)
user-create NAME="" EMAIL="":
    #!/usr/bin/env bash
    if [ -z "{{NAME}}" ] || [ -z "{{EMAIL}}" ]; then
        uv run python cli.py user:create
    else
        uv run python cli.py user:create -n "{{NAME}}" -e "{{EMAIL}}"
    fi

# List all users
user-list:
    @echo "📋 Listing users..."
    uv run python cli.py user:list

# Start Docker containers
docker-up BUILD="":
    #!/usr/bin/env bash
    if [ "{{BUILD}}" = "build" ]; then
        docker-compose up --build -d
    else
        docker-compose up -d
    fi
    @echo "✅ Docker containers started"

# Stop Docker containers
docker-down VOLUMES="":
    #!/usr/bin/env bash
    if [ "{{VOLUMES}}" = "volumes" ]; then
        docker-compose down -v
    else
        docker-compose down
    fi

# View Docker logs
docker-logs SERVICE="":
    #!/usr/bin/env bash
    if [ -z "{{SERVICE}}" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f {{SERVICE}}
    fi

# Clean Python cache files
clean:
    @echo "🧹 Cleaning Python cache files..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @find . -type f -name "*.pyo" -delete 2>/dev/null || true
    @find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    @echo "✅ Cleaned"

# Install dependencies
install:
    uv sync

# Add a new dependency
add PACKAGE:
    uv add {{PACKAGE}}

# Run all database tests
test-db: db-test
    @echo "✅ Database tests passed"

# Full check (db + api health)
check: db-test health
    @echo "✅ All checks passed"

# Show environment info
info:
    @echo "📊 Environment Info:"
    @echo "Python: $(python --version)"
    @echo "UV: $(uv --version)"
    @echo "Database: $(grep DATABASE_URL .env | cut -d= -f2 | cut -d@ -f2 | cut -d/ -f1)"
