"""IANdb - AWS IAM database management package.

This package provides tools to download and manage AWS IAM definitions
in a local SQLite database.
"""
from .ian_db import IANdb

__all__ = ["IANdb"]
