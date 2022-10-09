from typing import List

import email_utils.gmail_client as client
import email_utils.email_labels as labels


def _list_threads_by_page(next_page_token=None):
    gmail = client.create_client()

    response = gmail.users().threads() \
        .list(userId='me', maxResults=500, pageToken=next_page_token) \
        .execute()
        
    threads = response.get('threads', [])
    next_page_token = response.get('nextPageToken')

    return threads, next_page_token


def list_all_threads() -> List:
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