# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


# Type aliases
ThreadId = str
MessageId = str
NextPageToken = str | None

class Message(BaseModel):
    msg_id: str  # ToDo: Use type alias
    sender: str
    body: str
    timestamp: int


# data structures
class RawThread(BaseModel):
    id: ThreadId
    messages: list[Message]


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
