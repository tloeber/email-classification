"""
This module defines the schemas for the data that we expect to receive from
the Gmail API. These schemas are used by Pydantic to parse the data, and to
raise an exception if the data cannot be coereced into the respective schema.

Note that these classes are data structures, not `real` classes: They expose
their data rather than behavior. (The behavior is defined in the `email_domain`
package, and is decoupled from the data schemas that particular email APIs use.)
"""

# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from pydantic import BaseModel


# Type aliases
ThreadId = str
MessageId = str
NextPageToken = str | None


# data structures
class RawThread(BaseModel):
    id: ThreadId
    messages: list[RawMessage]


class RawMessage(BaseModel):
    id: MessageId
    internalDate: int
    payload: MessagePayload
    

# *Inner* data structures
class MessagePayload:
    body: MessageBody
    headers: list[dict]
    parts: MIMEParts | None


class MIMEParts:
    body: MIMEBody


class MIMEBody:
    data: bytes  # Base64-encoded bytes


class MessageBody:
    data: str
