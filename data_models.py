# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from pydantic import BaseModel


class Message(BaseModel):
    msg_id: str  # ToDo: Use type alias
    sender: str

    @classmethod
    def from_api_response(cls, response: dict) -> Message:
        """Constructor that picks out relevant fields from API response."""
        return cls(
            msg_id=response['id'],
            sender=response['payload']['headers']['From'],
        )