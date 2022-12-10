## Local imports wouldn't work at the top of the file because they rely on
## modified system path. So they are in pytest_sessionstart().
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import

import sys
from pathlib import Path
import pytest


def pytest_sessionstart(session) -> None:
    """"This is run at the start of each test session."""

    # Add ludwig's root directory to path.
    # NOTE: It's not possible to use the variable we define for this in
    # absolute_paths.py, because this module is not in the path yet. So we are
    # basically facing a chicken and egg problem, and  solve it by getting Path
    # from scratch again.
    LUDWIG_ROOT_DIR: Path = (
        Path(__file__).parent  # tests/
        .parent  # ludwig/
        .resolve()
    )

    sys.path.append(
        str(LUDWIG_ROOT_DIR)
    )
