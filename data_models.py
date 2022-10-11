# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from pydantic import BaseModel


# Type aliases
ThreadId = str
MessageId = str
NextPageToken = str | None

class Message(BaseModel):
    msg_id: str  # ToDo: Use type alias
    sender: str
    body: str
