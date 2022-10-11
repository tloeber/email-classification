# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
import logging
import pickle 

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


def _get_thread_details(
    thread_id: ThreadId
) -> tuple[MessageId, list[MessageId], list[dict]]:
    """
    Given a thread id, this returns:
    - id of message replied to;
    - list of ids of messages to discard
    """
    def _get_sender(msg: dict):
        headers = msg['payload']['headers']
        # Headers is a list of dicts with keys `name` and `value`
        for header in headers:
            if header['name'] == 'From':
                return header['value']


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
                body=msg['payload']['body']['data']
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
    msg_replied_to = thread.find_msg_replied_to()
    msgs_to_discard = thread.find_messages_to_discard()
    return msg_replied_to, msgs_to_discard, dlq


def assign_msg_labels(
    thread_ids: list[ThreadId]
) -> tuple[list[ThreadId], list[ThreadId]]:

    """
    Find messages replied to and messages to discard for analysis because
    they were sent after first reply. 
    Returns a list of msg ids for each of these categories.
    """
    logging.info('Assigning message labels')
    msgs_replied_to = []
    msgs_to_discard = []
    combined_dlq = []

    for thread_id in thread_ids:
        replied_to, discard, dlq = _get_thread_details(thread_id)

         # `replied_to` will be None if no reply was elicited. Ignore these.
        if replied_to:
            msgs_replied_to.append(replied_to)

        #  `discard` will be None if no reply was elicited. Don't need to drop 
        # anything in this case.
        if discard:
            msgs_to_discard.extend(discard)

        if len(dlq) > 0:
            combined_dlq.extend(dlq)

    return msgs_replied_to, msgs_to_discard, combined_dlq
