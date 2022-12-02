# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

from abc import ABC, abstractmethod


class RawMessageInterface(ABC):
    """
    Contract for RawMessage that the pydantic dataclass for every API response
    has to implement.

    While the structure of the API responses will likely differ
    between APIs, we can easily implement this interface by adding
    properties for fields needed (namely sender and body) that get these fields
    from the API-specific location.
    """

    @property
    @abstractmethod
    def sender(self) -> str | None:
        """Check in various places to find an email's sender."""

    @property
    @abstractmethod
    def body_as_text(self) -> str | None:
        """Get body, decode it, and convert from html to text."""

    @abstractmethod
    def json(self) -> str:
        """
        Convert message to json. Implemented by default for pydantic subclasses,
        so don't have to explicitly implement.
        """
