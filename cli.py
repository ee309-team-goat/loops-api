#!/usr/bin/env python3
"""
CLI commands for Loops API project.
Usage: uv run python cli.py <command> [options]
"""

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_command(cmd: list[str], description: str = "") -> int:
    """Run a shell command and return the exit code."""
    if description:
        print(f"→ {description}")
    print(f"  Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def dev_server(args):
    """Start the development server with auto-reload."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from .env.example...")
        example = Path(".env.example")
        if example.exists():
            env_file.write_text(example.read_text())
            print("✓ Created .env file\n")
        else:
            print("❌ .env.example not found. Please create a .env file manually.\n")
            return 1

    print("🚀 Starting development server...")
    return run_command(["uv", "run", "python", "src/main.py"])


def db_migrate(args):
    """Run database migrations (upgrade to head)."""
    print("📦 Running database migrations...")
    return run_command(
        ["uv", "run", "alembic", "upgrade", "head"],
        "Upgrading database to latest version"
    )


def db_rollback(args):
    """Rollback the last database migration."""
    steps = args.steps if hasattr(args, 'steps') else 1
    print(f"↩️  Rolling back {steps} migration(s)...")
    return run_command(
        ["uv", "run", "alembic", "downgrade", f"-{steps}"],
        f"Rolling back {steps} migration(s)"
    )


def db_revision(args):
    """Create a new database migration."""
    if not args.message:
        print("❌ Error: Migration message is required")
        print("Usage: uv run python cli.py db:revision -m 'Your message here'")
        return 1

    print(f"📝 Creating new migration: {args.message}")
    cmd = ["uv", "run", "alembic", "revision"]
    if args.autogenerate:
        cmd.append("--autogenerate")
    cmd.extend(["-m", args.message])
    return run_command(cmd)


def db_history(args):
    """Show database migration history."""
    print("📜 Migration history:")
    return run_command(["uv", "run", "alembic", "history"])


def db_current(args):
    """Show current database revision."""
    print("📍 Current database revision:")
    return run_command(["uv", "run", "alembic", "current"])


def db_reset(args):
    """Reset database (downgrade all and upgrade to head)."""
    if not args.yes:
        response = input("⚠️  This will reset the database. Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return 0

    print("🔄 Resetting database...")
    result = run_command(
        ["uv", "run", "alembic", "downgrade", "base"],
        "Downgrading to base"
    )
    if result != 0:
        return result

    return run_command(
        ["uv", "run", "alembic", "upgrade", "head"],
        "Upgrading to head"
    )


def docker_up(args):
    """Start Docker containers."""
    cmd = ["docker-compose", "up"]
    if args.build:
        cmd.append("--build")
    if args.detach:
        cmd.append("-d")

    print("🐳 Starting Docker containers...")
    return run_command(cmd)


def docker_down(args):
    """Stop Docker containers."""
    cmd = ["docker-compose", "down"]
    if args.volumes:
        cmd.append("-v")

    print("🛑 Stopping Docker containers...")
    return run_command(cmd)


def docker_logs(args):
    """View Docker container logs."""
    cmd = ["docker-compose", "logs"]
    if args.follow:
        cmd.append("-f")
    if args.service:
        cmd.append(args.service)

    return run_command(cmd, "Viewing Docker logs")


def setup_project(args):
    """Set up the project (install deps, create .env, run migrations)."""
    print("🔧 Setting up Loops API project...\n")

    # Install dependencies
    result = run_command(["uv", "sync"], "Installing dependencies")
    if result != 0:
        return result

    # Create .env if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        example = Path(".env.example")
        if example.exists():
            env_file.write_text(example.read_text())
            print("\n✓ Created .env file from .env.example")
            print("⚠️  Don't forget to update DATABASE_URL in .env\n")
        else:
            print("\n⚠️  .env.example not found\n")
    else:
        print("\n✓ .env file already exists\n")

    # Ask if they want to run migrations
    response = input("Run database migrations now? (y/N): ")
    if response.lower() == 'y':
        result = run_command(
            ["uv", "run", "alembic", "upgrade", "head"],
            "\nRunning database migrations"
        )
        if result != 0:
            print("\n⚠️  Migrations failed. Make sure your DATABASE_URL is correct in .env")
            return result

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("  1. Update DATABASE_URL in .env file")
    print("  2. Run migrations: uv run python cli.py db:migrate")
    print("  3. Start dev server: uv run python cli.py dev")
    return 0


def test_db_connection(args):
    """Test database connection."""
    print("🔌 Testing database connection...")
    test_script = """
import asyncio
from app.database import engine
from sqlalchemy import text

async def test_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return 0
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1

exit(asyncio.run(test_connection()))
"""

    result = subprocess.run(
        ["uv", "run", "python", "-c", test_script],
        capture_output=False
    )
    return result.returncode


def health_check(args):
    """Check if the API server is running and healthy."""
    print("🏥 Checking API health...")
    test_script = """
import httpx
import sys

try:
    response = httpx.get("http://localhost:8000/health", timeout=5.0)
    if response.status_code == 200:
        print("✅ API is healthy!")
        print(f"   Response: {response.json()}")
        sys.exit(0)
    else:
        print(f"⚠️  API returned status {response.status_code}")
        sys.exit(1)
except httpx.ConnectError:
    print("❌ Cannot connect to API at http://localhost:8000")
    print("   Make sure the server is running: uv run python cli.py dev")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
"""

    # Check if httpx is available
    check_httpx = subprocess.run(
        ["uv", "run", "python", "-c", "import httpx"],
        capture_output=True
    )

    if check_httpx.returncode != 0:
        print("Installing httpx for health check...")
        subprocess.run(["uv", "add", "httpx"])

    result = subprocess.run(
        ["uv", "run", "python", "-c", test_script],
        capture_output=False
    )
    return result.returncode


def create_user(args):
    """Create a new user via CLI."""
    print("👤 Creating new user...")

    name = args.name
    email = args.email

    # Interactive mode if args not provided
    if not name:
        name = input("Enter name: ")
    if not email:
        email = input("Enter email: ")

    if not name or not email:
        print("❌ Name and email are required")
        return 1

    create_script = f"""
import asyncio
from app.database import get_session
from app.models.user import UserCreate
from app.services.user_service import UserService

async def create_user():
    async for session in get_session():
        try:
            user_service = UserService(session)
            user_data = UserCreate(name="{name}", email="{email}")
            user = await user_service.create_user(user_data)
            print(f"✅ User created successfully!")
            print(f"   ID: {{user.id}}")
            print(f"   Name: {{user.name}}")
            print(f"   Email: {{user.email}}")
            return 0
        except Exception as e:
            print(f"❌ Error creating user: {{e}}")
            return 1

exit(asyncio.run(create_user()))
"""

    result = subprocess.run(
        ["uv", "run", "python", "-c", create_script],
        capture_output=False
    )
    return result.returncode


def list_users(args):
    """List all users in the database."""
    print("📋 Listing users...\n")

    list_script = """
import asyncio
from app.database import get_session
from app.services.user_service import UserService

async def list_users():
    async for session in get_session():
        try:
            user_service = UserService(session)
            users = await user_service.get_users(skip=0, limit=100)

            if not users:
                print("No users found.")
                return 0

            print(f"Found {len(users)} user(s):\\n")
            for user in users:
                print(f"  • {user.name} ({user.email})")
                print(f"    ID: {user.id}")
                print(f"    Created: {user.created_at}")
                print()
            return 0
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return 1

exit(asyncio.run(list_users()))
"""

    result = subprocess.run(
        ["uv", "run", "python", "-c", list_script],
        capture_output=False
    )
    return result.returncode


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Loops API CLI - Manage your FastAPI project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python cli.py setup              # Initial project setup
  uv run python cli.py dev                # Start development server
  uv run python cli.py db:migrate         # Run database migrations
  uv run python cli.py db:revision -m "Add users" --auto
  uv run python cli.py user:create        # Interactive user creation
  uv run python cli.py user:create -n "John" -e "john@example.com"
  uv run python cli.py docker:up -d       # Start Docker in detached mode
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Setup
    subparsers.add_parser('setup', help='Set up the project (install deps, create .env, run migrations)')

    # Development
    subparsers.add_parser('dev', help='Start development server with auto-reload')

    # Health & Testing
    subparsers.add_parser('health', help='Check API health endpoint')
    subparsers.add_parser('db:test', help='Test database connection')

    # Database migrations
    subparsers.add_parser('db:migrate', help='Run database migrations (upgrade to head)')

    rollback_parser = subparsers.add_parser('db:rollback', help='Rollback database migration(s)')
    rollback_parser.add_argument('-s', '--steps', type=int, default=1, help='Number of migrations to rollback (default: 1)')

    revision_parser = subparsers.add_parser('db:revision', help='Create a new database migration')
    revision_parser.add_argument('-m', '--message', required=True, help='Migration message')
    revision_parser.add_argument('--auto', '--autogenerate', dest='autogenerate', action='store_true',
                                help='Auto-generate migration from models')

    subparsers.add_parser('db:history', help='Show migration history')
    subparsers.add_parser('db:current', help='Show current database revision')

    reset_parser = subparsers.add_parser('db:reset', help='Reset database (downgrade all and upgrade to head)')
    reset_parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')

    # Docker
    docker_up_parser = subparsers.add_parser('docker:up', help='Start Docker containers')
    docker_up_parser.add_argument('-b', '--build', action='store_true', help='Build images before starting')
    docker_up_parser.add_argument('-d', '--detach', action='store_true', help='Run in detached mode')

    docker_down_parser = subparsers.add_parser('docker:down', help='Stop Docker containers')
    docker_down_parser.add_argument('-v', '--volumes', action='store_true', help='Remove volumes')

    docker_logs_parser = subparsers.add_parser('docker:logs', help='View Docker container logs')
    docker_logs_parser.add_argument('-f', '--follow', action='store_true', help='Follow log output')
    docker_logs_parser.add_argument('service', nargs='?', help='Specific service to show logs for')

    # User management
    user_create_parser = subparsers.add_parser('user:create', help='Create a new user')
    user_create_parser.add_argument('-n', '--name', help='User name')
    user_create_parser.add_argument('-e', '--email', help='User email')

    subparsers.add_parser('user:list', help='List all users')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        'setup': setup_project,
        'dev': dev_server,
        'health': health_check,
        'db:test': test_db_connection,
        'db:migrate': db_migrate,
        'db:rollback': db_rollback,
        'db:revision': db_revision,
        'db:history': db_history,
        'db:current': db_current,
        'db:reset': db_reset,
        'docker:up': docker_up,
        'docker:down': docker_down,
        'docker:logs': docker_logs,
        'user:create': create_user,
        'user:list': list_users,
    }

    handler = handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            return 130
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
