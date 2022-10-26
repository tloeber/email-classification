import logging

from .core_client import CoreClient
from ..data_schemas.gmail_api import Message, NextPageToken, ThreadId, MessageId
from ..email_domain.thread import EmailThread


logger = logging.getLogger(__name__)

class ThreadClient:
    
    def __init__(self, core_client: CoreClient) -> None:
        self.core_client = CoreClient()

    def get_thread_with_details(
        self, thread_id: ThreadId
    ) -> tuple[EmailThread, list[dict]]:
        """
        Given a thread id, create list of detailed EmailThread objects.
        """

        response = self.__get_thread_client() \
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
                    body=_get_body_as_text(msg),
                    timestamp=int(msg['internalDate'],)
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

    def list_all_thread_ids(self, query: str | None = None) -> list[ThreadId]:
        """
        Get list of thread ids for a custom query, e.g. by date range. If more
        than one page is returned, this handels pagination under the hood.
        """
        all_thread_ids = []
        next_page_token = None
        while True:
            thread_ids, next_page_token = self._list_thread_ids_paginated(
                next_page_token=next_page_token, 
                query=query
            )
            all_thread_ids.extend(thread_ids)

            # Exit loop once no more pages are left
            if not next_page_token:
                return all_thread_ids

    def _list_thread_ids_paginated(
        self,
        next_page_token: NextPageToken | None = None,
        query: str | None = None,
    ) -> tuple[list[ThreadId], NextPageToken]:
        """Get list of thread ids for a single page"""

        logger.info('Listing threadIDs for a single page.')        
        response =  self.__get_thread_client() \
            .list(
                userId='me', 
                maxResults=500,
                includeSpamTrash=False, 
                q=query,
                pageToken=next_page_token, 
            ) \
            .execute()
            
        # Only keep id of each thread (for retrieving thread details later)
        threads = response.get('threads', [])
        thread_ids = [thread['id'] for thread in threads]
        next_page_token = response.get('nextPageToken')
        return thread_ids, next_page_token
    
    def __get_thread_client(self):
        gmail_client = self.gmail_client.get_authenticated_client()
        return gmail_client.users().threads()
