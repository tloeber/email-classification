"""
This package defines the schemas for the data that we expect to receive from
the Gmail API. These schemas are used by Pydantic to parse the data, and to
raise an exception if the data cannot be coereced into the respective schema.

This specific module defines all schemas for *getting* a particular thread.

Note that these classes are data structures, not `real` classes: They expose
their data, rather than exposing behavior while encapsulating data. (The
behavior is defined in the `email_domain` package, and is decoupled from the
data schemas that particular email APIs use.)

The order of class definitions is significant: Start with innermost data
classes! Otherwise, Pydantic raises an error (though it may still  be
possible to make it work by explicitly updating forward references.)
"""

# Due to the large number of inner data classes - which result from the nesting
# of the different parts of an email object – it seems excessive to add a
# docstring to each. So turn off this pylint warning for the entire module.
# pylint: disable=missing-class-docstring

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

import base64
import json
from typing import Final, ClassVar

from bs4 import BeautifulSoup
from pydantic import BaseModel

from data_schemas.interface import RawMessageInterface
from data_schemas.gmail.simple_types import MessageId, ThreadId
from utils.dlq import DLQ


# Customize Pydantic base model
# =============================

class CustomBaseModel(BaseModel):
    """
    Configured the validation behavior to *allow but ignore* extra fields
    passed to constructor. Also, just in case, make instances immutable.
    """
    class Config:
        """Configures validation behavior."""
        extra = 'ignore'
        frozen = 'true'


# *Inner* data structures
# =======================

class MIMEBody(CustomBaseModel):
    data: bytes  # Base64-encoded bytes


class MIMEParts(CustomBaseModel):
    """
    This contains child MIME messsage parts for *container* MIME messsage parts.
    For non-container MIME message part types, this field is empty.
    """
    mime_body: MIMEBody | None


class MessageBody(CustomBaseModel):
    # Data may be empty for MIME container types that have no message body or
    # when the body data is sent as a separate attachment.
    data: str | None  # Or is it Literal[{'size': 0}] if it's missing?


class MessagePayload(CustomBaseModel):
    body: MessageBody | None  # May be `None` for container MIME message parts
    headers: list[dict]
    mime_parts: MIMEParts | None
    # Todo: Consider leveraging polymorphism, depending on value of 'mimeType'
    mimeType: str


class RawGmailMessage(RawMessageInterface):
    """
    Even though this is a data structure rather than a proper class, I still
    decided to implement custom getter logic here. Rationale:
    - These methods do not fit into the domain representation
      (email_domain.Message) because they may differ between email APIs, rather
      than being a characteristic of our domain.
    - While we could introduce another class that parses raw Gmail messages, at
      this point it does not seem worth the extra complexity that this would
      create.
    """

    id: MessageId
    internalDate: int  # UNIX timestamp
    payload: MessagePayload

    dlq: ClassVar = DLQ(name="RawGmailMessage")

    @property
    def sender(self) -> str | None:
        """
        Return sender if found. Otherwise raise Exception.
        """
        for header in self.payload.headers:
            if header['name'] == 'From':
                return header['value']

        # If we end up here, header was not found
        self.dlq.add_message(
            problem="No sender found in message payload.",
            data=self.json()
        )
        return None

    @property
    def body_as_text(self) -> str | None:
        """Get body, decode it, and convert from html to text."""
        # Todo: Consider using polymorphism to simplify logic of getting
        # sender and body for different  MIME types.

        # Check if the default body location contains any data
        if self.payload.body and (self.payload.body.data is not None):
            body_encoded = self.payload.body.data

        # Depending on protocol, body may be located elsewhere
        elif self.payload.mime_parts:
            for part in self.payload.mime_parts:
                if part.body and part.body.data is not None:
                    body_encoded = part.body.data
                    break

        # If we found email body, decode it
        if body_encoded:
            body_html: bytes = base64.urlsafe_b64decode(body_encoded)
            # ToDo: Explicitly specify bs parser
            return BeautifulSoup(body_html, features='html.parser').get_text()

        # If we didn't find body, return None
        else:
            self.dlq.add_message(
                problem="No body found in message payload.",
                data=self.json()
            )
            return None



# Top-level data structure
# ========================

class RawGmailThread(CustomBaseModel):
    """Scheme of response to a get-threads API call."""
    id: ThreadId
    messages: list[RawGmailMessage]
