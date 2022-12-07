"""
This specific module defines type aliases for simple types. Their function is to
make type hints more informative (especially for *return* types, where we do
not have an accompanying variable name that can fulfill this purpose.)

These type aliases live in a dedicated module because they are used by both
other modules in this package.
"""

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations
from typing import TypeAlias

# Type aliases
# ============
ThreadId: TypeAlias = str
MessageId: TypeAlias = str
NextPageToken: TypeAlias = str | None
