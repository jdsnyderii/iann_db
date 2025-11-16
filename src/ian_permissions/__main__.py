"""Module CLI entrypoint.

Allows running with `python -m ian_permissions` when `src` is on PYTHONPATH.
"""
from .ian_db_cli import main

if __name__ == '__main__':
    main()
