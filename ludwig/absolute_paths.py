"""Keep track of absolute paths to make imports more stable."""

from pathlib import Path

LUDWIG_ROOT_DIR: Path = (
    Path(__file__).parent.resolve()
)
print()
