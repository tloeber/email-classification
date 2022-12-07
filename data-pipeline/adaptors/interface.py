# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

from abc import ABC, abstractmethod


class MessageAdaptorInterface(ABC):
    """
    Interface that adapted RawMessages need to implement.

    While the structure of the API responses will likely differ between the
    different email provider's APIs, we will create an adapter for each of these
     APIs, all of which will implement the same interface.
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
        Convert message to json.

        Implemented by default for pydantic subclasses, so we can just call
        that.
        """
