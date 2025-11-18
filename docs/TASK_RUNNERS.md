# Task Runners - Best Practices & Comparison

## TL;DR - What Should You Use?

**✅ Final Setup (Clean & Modern):**

1. **Just** - Modern task runner for daily tasks
2. **Python CLI (cli.py)** - For complex operations

## Current Setup

Your project uses **2 complementary tools** (no duplication):

### 1. Just (justfile) ⭐ RECOMMENDED

```bash
just dev                    # Start server
just migrate                # Run migrations
just revision "Add field"   # Create migration
just check                  # Run all health checks
```

**Pros:**

- ✅ Cross-platform
- ✅ Better syntax than Make (no tabs!)
- ✅ Built-in command listing
- ✅ Supports parameters
- ✅ Can confirm dangerous operations
- ✅ Modern, actively maintained

**Cons:**

- ❌ Requires installation (`brew install just`)
- ❌ Less familiar to older devs

**Best for:** Projects that need a task runner with logic/parameters

---

### 2. Python CLI (cli.py)

```bash
uv run python cli.py dev
uv run python cli.py db:revision -m "message" --auto
uv run python cli.py user:create -n "John" -e "john@example.com"

# Or after install:
loops dev
loops user:create
```

**Pros:**

- ✅ Cross-platform
- ✅ Complex logic and validations
- ✅ Can use async operations
- ✅ Full access to your app's code
- ✅ Interactive prompts
- ✅ Can be installed as CLI tool

**Cons:**

- ❌ Verbose to run (unless installed)
- ❌ More code to maintain

**Best for:** Complex operations, database operations, interactive commands

---

## Industry Best Practices (2024-2025)

### What Big Projects Use:

| Project           | Task Runner              | Why                     |
| ----------------- | ------------------------ | ----------------------- |
| **Django**        | Custom manage.py         | Complex framework needs |
| **FastAPI**       | pyproject.toml scripts   | Simple, modern          |
| **Poetry**        | pyproject.toml scripts   | Built-in to tool        |
| **Rust projects** | Just                     | Modern, cross-platform  |
| **Node.js**       | package.json scripts     | Built-in to ecosystem   |
| **Make**          | Linux kernel, C projects | Traditional, well-known |

### Modern Python Project Trend:

```
pyproject.toml scripts (simple)
          ↓
         Just (medium complexity)
          ↓
    Python CLI with Click/Typer (complex)
```

---

## My Recommendations

### For Your Project (FastAPI + UV):

**Best Practice - Just + Python CLI:** ✅

```bash
# Daily dev work - Just (modern, clean)
just dev
just migrate
just revision "Add field"

# Complex operations - Python CLI
uv run python cli.py user:create
uv run python cli.py db:reset

# Alternative - Make (if team prefers)
make dev
make db-migrate
```

### Which to Use When:

**Just** (recommended):

- ✅ Starting dev server
- ✅ Running migrations
- ✅ Running tests
- ✅ Commands with parameters
- ✅ Chained operations
- ✅ Commands needing confirmation
- ✅ All simple to medium tasks

**Python CLI** (`cli.py`):

- ✅ Interactive operations
- ✅ Database seeding
- ✅ User management
- ✅ Complex validation
- ✅ Anything async
- ✅ Operations needing app imports

**Makefile**:

- ✅ If team already uses Make
- ✅ Simple commands on Unix systems
- ❌ Skip for new projects (use Just instead)

---

## What to Remove?

You have some duplication now. Here's what to keep:

### Minimal Setup (Recommended):

```
justfile        ← Modern task runner for all simple tasks ⭐
cli.py          ← Python CLI for complex operations
```

**Remove:**

- `Makefile` - Replace with justfile
- `scripts/*.sh` - Redundant with above

### If Team Knows Make:

```
Makefile        ← Keep if team prefers
cli.py          ← Python CLI for complex operations
```

**Remove:**

- `justfile` - Not needed if using Make
- `scripts/*.sh` - Redundant

### Ultra-Minimal (Not Recommended):

```
cli.py          ← Python CLI for everything
```

(More typing required for simple tasks)

---

## Examples of Each Approach

### Just (Flexible & Clean):

```just
# justfile
dev:
    @echo "Starting server..."
    uv run dev

test *ARGS:
    pytest {{ARGS}}
```

```bash
just dev
just test tests/api/
```

### Python CLI (Complex):

```python
# cli.py with Typer (cleaner than argparse)
import typer

app = typer.Typer()

@app.command()
def dev():
    """Start development server"""
    uvicorn.run("app.main:app", reload=True)
```

---

## Migration Path

If you want to **modernize** from what I created:

### Step 1: Start using UV scripts

```bash
# Old
make dev

# New
uv run dev
```

### Step 2: Try Just

```bash
brew install just
just dev
```

### Step 3: Remove redundant tools

- Keep: `pyproject.toml`, `cli.py`, `justfile`
- Remove: `Makefile`, `scripts/`

### Step 4: (Optional) Upgrade CLI to Typer

Makes `cli.py` cleaner and more maintainable.

---

## ✅ IMPLEMENTED - Current Setup

**Your project now uses:**

1. ✅ **Just** - For all simple/medium tasks
2. ✅ **cli.py** - For complex operations only
3. ✅ **Removed** - Makefile (was redundant)
4. ✅ **Removed** - scripts/ folder (was redundant)

**Commands become:**

```bash
# Simple tasks (Just)
just dev
just migrate
just rollback

# Medium tasks (Just with params)
just revision "Add field"
just check
just user-create "John" "john@example.com"

# Complex tasks (Python CLI)
uv run python cli.py db:reset
uv run python cli.py user:create  # Interactive mode
```

This gives you the best of all worlds:

- Simple tasks are quick to type with Just
- Complex tasks have full Python power
- Cross-platform compatible
- Modern tooling
- No duplication
- Clean, readable syntax

---

## Installing Just

```bash
# macOS
brew install just

# Linux
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# Windows
scoop install just
# or
cargo install just
```

Then:

```bash
just --list  # See all commands
just dev     # Run command
```

Much nicer than Make! 🎉
