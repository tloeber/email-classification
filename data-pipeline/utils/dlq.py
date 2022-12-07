"""
Implements a dead-letter queue to store messages which were not processed
successfully.
"""

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

from typing import Final, NoReturn, Any, TypeAlias
from datetime import datetime
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Define struucture of a DLQ messsage
DLQMessage: TypeAlias = dict[str, Any]

class DLQ:
    """
    Dead letter queue to store messages that failed to process correctly.
    """
    def __init__(self, name: str | None = None) -> None:
        self._name: str | None = name
        self._creation_datetime: Final[str] = f'{datetime.now()}'
        self._messages: list[DLQMessage] = []

    @property
    def name(self) -> str | None:
        return self._name

    def add_message(
        self,
        problem: str,
        exception: Exception | None = None,
        data: str | None = None,
    ) -> None:
        """Add message to DLQ."""
        self._messages.append(
            {
                "problem": problem,
                "exception": str(exception),
                "timestamp": f'{datetime.now()}',
                'data': data,
            }
        )

    def __str__(self) -> str:
        """ String representation will be used to persist DLQ."""
        dlq_as_dict: dict[str, str | list[DLQMessage] | None] = {
            'name': self._name,
            'creationDateTime': self._creation_datetime,
            'messages': self._messages
        }
        return json.dumps(dlq_as_dict)

    def persist(
        self,
        directory: Path | None = None,
        file_name: str | None = None,
    ) -> None:
        """Save DLQ to disk, so we can analyze it after execution finished."""

        def _validate_filename(file_name: str) -> None | NoReturn:
            file_extension = Path(file_name).suffix
            if file_extension != '.json':
                raise ValueError(
                    'Expected filename to end in `.json` but instead found '
                    f'{file_extension}.'
                )
            else:
                return None

        if file_name:
            _validate_filename(file_name)
        else:
            # Create  default filename, if not passed
            file_name: str = \
                f'DLQ-{self._name or "unknown"}-{self._creation_datetime}'

        # If directory is not specified, use the current working directory.
        if not directory:
            dlq_path = Path(file_name)
        else:
            dlq_path = directory / file_name

        with open(dlq_path, 'w') as file:
            json.dump(
                obj=str(self),  # Using __str__() defined above
                fp=file
            )
        logger.info(f"Saved DLQ {self._name} to {directory}.")
