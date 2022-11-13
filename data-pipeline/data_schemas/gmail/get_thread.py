"""
This package defines the schemas for the data that we expect to receive from
the Gmail API. These schemas are used by Pydantic to parse the data, and to
raise an exception if the data cannot be coereced into the respective schema.

This specific module defines all schemas for *getting* a particular thread.

Note that these classes are data structures, not `real` classes: They expose
their data rather than behavior. (The behavior is defined in the `email_domain`
package, and is decoupled from the data schemas that particular email APIs use.)
"""

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

import base64
import json

from bs4 import BeautifulSoup
from pydantic import BaseModel

from data_schemas.gmail.simple_types import MessageId, ThreadId
from utils.dlq import DLQ


# Customize Pydantic base model
# =============================

class CustomBaseModel(BaseModel):
    """
    Configured the validation behavior to *allow but ignore* extra fields
    passed to constructor
    """
    class Config:
        extra = 'ignore'


# Top-level data structure
# ========================

class RawThread(CustomBaseModel):
    """Scheme of response to a get-threads API call."""
    id: ThreadId
    messages: list[RawMessage]


# *Inner* data structures
# =======================

# Todo: Create interface for returning sender & body that this class implements
class RawMessage(CustomBaseModel):
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
    dlq: DLQ  # To hold messages that did not conform to the expected schema

    class Config:
        # Since DLQ is not a pydantic data type, we need to explicitly allow
        # using a normal class as a type.
        arbitrary_types_allowed = True


    def get_sender(self) -> str | None:
        """
        Return sender if found. Otherwise, add message to DLQ and return None.
        """
        for header in self.payload.headers:
            if header['name'] == 'From':
                return header['value']

        # If we end up here, header was not found
        self.dlq.add_message(
            problem="No sender found in message payload.",
            data=json.dumps(
                {'id': self.id, 'payload': self.payload}
            )
        )
        return None


    def get_body_as_text(self) -> str | None:
        """Get body, decode it, and convert from html to text."""
        # Todo: Consider using polymorphism to simplify logic of getting
        # sender and body for different  MIME types.

        # Check if the default body location contains any data
        if self.payload.body and (self.payload.body.data is not None):
            body_encoded = self.payload.body.data

        # Depending on protocol, body may be located elsewhere
        elif self.payload.parts:
            for part in self.payload.parts:
                if part.body and part.body.data is not None:
                    body_encoded = part.body.data
                    break

        # If we found email body, decode it
        try:
            body_html = base64.urlsafe_b64decode(body_encoded)
            # ToDo: Explicitly specify bs parser
            return BeautifulSoup(body_html, features='html.parser').get_text()

        # If we didn't find body, add msg to DLQ and return None
        except NameError:
            self.dlq.add_message(
                problem="No body found",
                data=self.json()
            )
            # NOTE: Used to return empty string!
            return None


class MessagePayload(CustomBaseModel):  # pylint: disable=missing-class-docstring
    body: MessageBody | None  # May be `None` for container MIME message parts
    headers: list[dict]
    parts: MIMEParts | None


class MessageBody(CustomBaseModel):  # pylint: disable=missing-class-docstring
    # Data may be empty for MIME container types that have no message body or
    # when the body data is sent as a separate attachment.
    data: str | None


class MIMEParts(CustomBaseModel):
    """
    This contains child MIME messsage parts for *container* MIME messsage parts.
    For non-container MIME message part types, this field is empty.
    """
    body: MIMEBody | None


class MIMEBody(CustomBaseModel):  # pylint: disable=missing-class-docstring
    data: bytes  # Base64-encoded bytes
