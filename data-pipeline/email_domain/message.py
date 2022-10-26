# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations 
import logging
import base64
from bs4 import BeautifulSoup

from ..data_schemas.gmail_api import RawMessage
from ..utils.dlq import DLQ

logger = logging.getLogger(__name__)


class Message:

    def __init__(self, msg: RawMessage, dlq: DLQ):
        self.timestamp = msg['timestamp']
        self.dlq: DLQ = dlq
        self.sender = self.__get_sender(msg, dlq=dlq)
        self.body = self.__get_body_as_text(msg)
        
    def __get_sender(self, msg: dict, dlq: list) -> str | None:
        headers = msg['payload']['headers']
        # Headers is a list of dicts with keys `name` and `value`
        for header in headers:
            if header['name'] == 'From':
                return header['value']
        
        # Handle failure
        self.dlq.add_message(
            problem="No sender found",
            msg=msg
        )
        return None

    def __get_body_as_text(msg: dict, dlq) -> str | None:
        """Get body, decode it, and convert from html to text."""
        if 'data' in msg['payload']['body'].keys():
            body_encoded = msg['payload']['body']['data']
        
        # Depending on protocol, body may be located elsewhere
        elif 'parts' in msg['payload'].keys():
            for part in msg['payload']['parts']:
                if 'data' in part['body'].keys():
                    body_encoded = part['body']['data']
                    break
            # If we didn't find body in parts
            else:
                return None
        # If message neither contains `data` nor `parts`
        else:
            return None
        
        if body_encoded is not None:
            body_html = base64.urlsafe_b64decode(body_encoded)
            #  ToDo: Explicitly specify bs parser
            return BeautifulSoup(body_html, features='html.parser').get_text()
        
        # Handle failure
        else:
            dlq.add_message(
            problem="No body found",
            msg=msg
        )
        # NOTE: Used to return empty string!
        return None

