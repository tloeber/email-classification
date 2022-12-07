# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

from typing import Final
import logging

from data_schemas.gmail.get_thread import RawGmailMessage as RawGmailMessage

logger = logging.getLogger(__name__)

class Message:
    """
    Domain representation of an email message.

    Note that this class could currently also be represented by a data structure
    (e.g., dataclass or pydantic class) rather than a `proper` class, because
    the only methods it exposes could equally (or even better) be represented
    as attributes (sender and body), and because I decided to move other logic
    (gettting body and sender) to the respective data classes (`RawGmailMessage`),
    since it is specific to the particular scheme we get from a particular API.

    However, I still keep `Message` as a traditional class both
    for symmetry with the other domain class, EmailThread, and also because
    we may want to perform operations on a message in the future. The fact that
    all such operations we currently need are all performed on an EmailThread
    is merely coincidental.
    """

    def __init__(
        self,
        sender: str | None,
        body_as_text: str | None,
        unix_timestamp: int | None,
    ):
        self._unix_timestamp: Final[int | None] = unix_timestamp
        self._sender: Final[str | None] = sender
        self._body_as_text: Final[str | None] = body_as_text

    # Constructors from *particular* raw message schemas.
    # So far, only implemented for Gmail.
    @classmethod
    def from_gmail(
        cls, raw_msg: RawGmailMessage,
    ):
        """
        Construct general email message from particular Gmail API response.
        """

        msg = cls(
            sender=raw_msg.sender(),
            body_as_text=raw_msg.body_as_text(),
            unix_timestamp=raw_msg.internalDate,
        )
        return msg

    @property
    def sender(self) -> str | None:
        """Get an email's sender."""
        return self._sender

    @property
    def body(self) -> str | None:
        """Get an email's body, converted to text."""
        return self._body_as_text
