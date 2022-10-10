# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
import logging

import email_utils.gmail_client as client
import email_utils.email_labels as labels
from data_models import Message, NextPageToken, ThreadId, EmailId
from domain_models.email_thread import EmailThread
    
    
def _list_threads_by_page(
    next_page_token: NextPageToken | None = None,
    query: str | None = None,
) -> tuple[list[ThreadId], NextPageToken]:

    gmail = client.create_client()

    response = gmail.users().threads() \
        .list(userId='me', maxResults=500, pageToken=next_page_token, q=query) \
        .execute()
        
    # Only keep id of each thread (for retrieving thread details later)
    threads = response.get('threads', [])
    thread_ids = [thread['id'] for thread in threads]
    next_page_token = response.get('nextPageToken')
    return thread_ids, next_page_token


def list_all_threads(query: str | None = None) -> list[ThreadId]:
    all_threads = []
    next_page_token = None
    while True:
        threads, next_page_token = _list_threads_by_page(
            next_page_token=next_page_token, 
            query=query
        )
        all_threads.extend(threads)

        # Exit loop once no more pages are left
        if not next_page_token:
            return all_threads


def _get_thread_details(thread_id: ThreadId) -> tuple[EmailId, list[EmailId]]:
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
    msgs = [
        Message(
            msg_id=msg['id'],
            sender=_get_sender(msg),
        ) \
        for msg in response['messages']
    ]

    thread = EmailThread(
        thread_id=thread_id, 
        messages=msgs,
    )
    msg_replied_to = thread.find_msg_replied_to()
    msgs_to_discard = thread.find_messages_to_discard()
    return msg_replied_to, msgs_to_discard


def assign_msg_labels(
    thread_ids: list[ThreadId]
) -> tuple[list[ThreadId], list[ThreadId]]:

    """
    Find messages replied to and messages to discard for analysis because
    they were sent after first reply. 
    Returns a list of msg ids for each of these categories.
    """
    msgs_replied_to = []
    msgs_to_discard = []
    for thread_id in thread_ids:
        replied_to, discard = _get_thread_details(thread_id)

         # `replied_to` will be None if no reply was elicited. Ignore these.
        if replied_to:
            msgs_replied_to.append(replied_to)

        #  `discard` will be None if no reply was elicited. Don't need to drop 
        # anything in this case.
        if discard:
            msgs_to_discard.extend(discard)


    return msgs_replied_to, msgs_to_discard


def main():
    # labels.list_labels()
    thread_ids = list_all_threads(query='After:2022/08/01')
    msgs_replied_to, msgs_to_discard = assign_msg_labels(thread_ids=thread_ids)
    print(
        len(msgs_replied_to),
        len(msgs_to_discard)
    )

if __name__ == '__main__':
    main()