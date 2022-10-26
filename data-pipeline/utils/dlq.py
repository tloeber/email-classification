"""
Implements a dead-letter queue to store messages which were not processed
successfully.
"""

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations
from datetime import datetime
import logging


class DLQ:
    """
    Dead letter queue to store messages that failed to process correctly.
    """
    def __init__(self, 
        logger: logging.Logger, 
        name: str = None
    ) -> None:
        self.logger = logger
        self.records: list[dict] = []
        self.name = name

    def add_message(
        self, 
        problem: str, 
        exception: Exception | None = None,
    ):
        self.logger.warning(f'{problem}. {exception}')
        self.records.append(
            {
                "problem": problem,
                "exception": str(exception),
                "timestamp": f'{datetime.now()}'
            }
        )
