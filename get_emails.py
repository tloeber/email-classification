# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations 

import email_utils.gmail_client as client
import email_utils.email_labels as labels
from data_models import Message 

    
def _list_threads_by_page(next_page_token=None) -> tuple[list, str]:
    gmail = client.create_client()

    response = gmail.users().threads() \
        .list(userId='me', maxResults=500, pageToken=next_page_token) \
        .execute()
        
    threads = response.get('threads', [])
    next_page_token = response.get('nextPageToken')

    return threads, next_page_token


def list_all_threads() -> list:
    all_threads = []
    next_page_token = None
    while True:
        threads, next_page_token = _list_threads_by_page(next_page_token)
        all_threads.extend(threads)

        # Exit loop once no more pages are left
        if not next_page_token:
            return all_threads


def main():
    labels.list_labels()
    threads = list_all_threads()
    # for thread in threads:
    #     print(thread)
    print(len(threads))

if __name__ == '__main__':
    main()