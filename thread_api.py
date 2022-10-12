# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
import logging
import pickle 

from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup

import email_utils.gmail_client as client
from data_models import Message, NextPageToken, ThreadId, MessageId
from domain_models.email_thread import EmailThread
    
    
def _list_thread_ids_paginated(
    next_page_token: NextPageToken | None = None,
    query: str | None = None,
) -> tuple[list[ThreadId], NextPageToken]:
    
    print('Listing threadIDs for a single page.')
    gmail = client.create_client()

    response = gmail.users().threads() \
        .list(userId='me', maxResults=500, pageToken=next_page_token, q=query) \
        .execute()
        
    # Only keep id of each thread (for retrieving thread details later)
    threads = response.get('threads', [])
    thread_ids = [thread['id'] for thread in threads]
    next_page_token = response.get('nextPageToken')
    return thread_ids, next_page_token


def list_all_thread_ids(query: str | None = None) -> list[ThreadId]:
    all_thread_ids = []
    next_page_token = None
    while True:
        thread_ids, next_page_token = _list_thread_ids_paginated(
            next_page_token=next_page_token, 
            query=query
        )
        all_thread_ids.extend(thread_ids)

        # Exit loop once no more pages are left
        if not next_page_token:
            return all_thread_ids


def _get_thread_with_details(
    thread_id: ThreadId
) -> tuple[EmailThread, list[dict]]:
    """
    Given a thread id, this returns:
    - id of message replied to;
    - list of ids of messages to discard
    """
    # ToDo: Add this to thread constructor or client class?

    def _get_sender(msg: dict) -> str | None:
        headers = msg['payload']['headers']
        # Headers is a list of dicts with keys `name` and `value`
        for header in headers:
            if header['name'] == 'From':
                return header['value']

    def _get_body_as_text(msg: dict) -> str:
        """Get body, decode it, and convert from html to text."""
        if 'data' in msg['payload']['body'].keys():
            body_encoded: bytes = msg['payload']['body']['data']
        
        # Depending on protocol, body may be located elsewhere
        elif 'parts' in msg['payload'].keys():
            for part in msg['payload']['parts']:
                if 'data' in part['body'].keys():
                    body_encoded = part['body']['data']
                    break
            # If we didn't find body, return empty string.
            else:
                return ''
        else:
            return ''

        body_html: str = urlsafe_b64decode(body_encoded)
        #  ToDo: Explicitly specify bs parser
        return BeautifulSoup(body_html, features='html.parser').get_text()
        


    gmail = client.create_client()

    response = gmail.users().threads() \
        .get(userId='me', id=thread_id) \
        .execute()
    
    # Validate message schema and drop fields not needed by converting each
    # message to a pydantic data object.
    msgs = []
    dlq = []

    for msg in response['messages']:        
        try:
            valid_msg = Message(
                msg_id=msg['id'],
                sender=_get_sender(msg),
                body=_get_body_as_text(msg)
            )
            msgs.append(valid_msg)

        # If validation fails, save to dead letter queue
        except Exception as e:
            problem_details = {
                'exception': e,
                'message': msg
            }
            dlq.append(problem_details)

    thread = EmailThread(
        thread_id=thread_id, 
        messages=msgs,
    )
    return thread, dlq
