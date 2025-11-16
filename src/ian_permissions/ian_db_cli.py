"""CLI for IANdb - AWS IAM database management.

This module provides a command-line interface for creating and managing
the AWS IAM SQLite database.
"""
import argparse
import sys
from . import IANdb


def create_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Create and manage AWS IAM SQLite database from iann0036/iam-dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create database with defaults
  python -m ian_permissions

  # Create with custom database path
  python -m ian_permissions --db-path /tmp/custom.db

  # Create with custom URL
  python -m ian_permissions --url https://example.com/iam.json

  # Both custom URL and path
  python -m ian_permissions --url https://example.com/iam.json --db-path /tmp/custom.db
        """
    )

    parser.add_argument(
        '--url',
        type=str,
        default=IANdb.DEFAULT_URL,
        help=f"URL to IAM definition JSON (default: {IANdb.DEFAULT_URL})"
    )

    parser.add_argument(
        '--db-path',
        type=str,
        default=IANdb.DEFAULT_DB,
        help=f"Path to SQLite database file (default: {IANdb.DEFAULT_DB})"
    )

    return parser


def main(args=None):
    """Main CLI entrypoint."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    try:
        print(f"Creating database from: {parsed_args.url}")
        print(f"Output database: {parsed_args.db_path}")
        print()

        IANdb.create(url=parsed_args.url, db_path=parsed_args.db_path)
        print("\n✓ Database created successfully!")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
