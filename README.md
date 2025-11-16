# IAN DB

This repository contains a small script to download the AWS IAM dataset and load it into a local SQLite database.

## Setup (venv)

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or use the provided Makefile:

```bash
make setup
```

## Run

Run the package as a module (recommended):

```bash
# Using Makefile (preferred - prevents __pycache__)
make module [--url <URL>] [--db-path <PATH>]

# Or directly with PYTHONPATH
PYTHONPATH=src python -m ian_permissions --help
```

CLI options:

```
--url URL           URL to IAM definition JSON (default: GitHub iann0036/iam-dataset)
--db-path DB_PATH   Path to SQLite database file (default: aws_iam_advanced.db)
```

## Development

Use the Makefile targets for development:

```bash
make setup       # Create venv and install dependencies
make module      # Run the package as a module
make clean-cache # Remove __pycache__ and .pyc files
make clean       # Remove venv and cache
```

## Python Cache Management

This project prevents `__pycache__` from being generated in the `src` directory through:

1. **PYTHONDONTWRITEBYTECODE=1** - Set in Makefile and `.env.local`
2. **Python -B flag** - Used when running modules via Make targets
3. **.gitignore** - Excludes `__pycache__/` if accidentally created

To manually clean up any remaining cache:

```bash
make clean-cache
```

## Notes

- `requirements.txt` contains the runtime dependency `requests`.
- The script creates tables if they don't exist; it also clears all tables before loading (so it replaces existing data).
- Package layout: `src/ian_permissions/` with `ian_db.py` containing the `IANdb` class.
