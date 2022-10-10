# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from pyexpat.errors import messages 

import email_utils.gmail_client as client
import email_utils.email_labels as labels
from data_models import NextPageToken, ThreadId, EmailId
from domain_models.email_thread import EmailThread
    
    
def _list_threads_by_page(
    next_page_token: NextPageToken | None = None
) -> tuple[list[ThreadId], NextPageToken]:

    gmail = client.create_client()

    response = gmail.users().threads() \
        .list(userId='me', maxResults=500, pageToken=next_page_token) \
        .execute()
        
    # Only keep id of each thread (for retrieving thread details later)
    threads = response.get('threads', []) \
        .get['id']
    next_page_token = response.get('nextPageToken')
    return threads, next_page_token


def list_all_threads() -> list[ThreadId]:
    all_threads = []
    next_page_token = None
    while True:
        threads, next_page_token = _list_threads_by_page(next_page_token)
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
    gmail = client.create_client()

    response = gmail.users().threads() \
        .get(userId='me', id=thread_id) \
        .execute()
    
    thread = EmailThread(
        thread_id=thread_id, 
        messages=response['messages']
    )
    msg_replied_to = thread.find_msg_replied_to
    msgs_to_discard = thread.find_messages_to_discard
    return msg_replied_to, msgs_to_discard


def main():
    labels.list_labels()
    threads = list_all_threads()
    # for thread in threads:
    #     print(thread)
    print(len(threads))

if __name__ == '__main__':
    main()