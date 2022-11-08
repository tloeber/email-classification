"""
This module provides a wrapper around the gmail API's thread functionalities. It
deals with raw data as they are returned by the API. Thus, it uses pydantic data
classes to model *data structures* that validate and parse the input, rather 
than dealing with traditional classes that primarily expose their behavior 
rather than their data.
 - and does not carry out
any transformations. Instead, the latter is handled by the DataTransformer 
class, which models the domain of email data for our ML use case.
"""

import logging

from .core_client import CoreClient
from data_schemas.gmail_api import (
    ThreadId, NextPageToken,
    RawThreadSummary, RawThreadsList, 
)


logger = logging.getLogger(__name__)

class ThreadClient:
    """
    API Documentation: 
    https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.threads.html
    """
    
    def __init__(self) -> None:
        # ThreadClient is *composed with* CoreClient
        self.core_client = CoreClient()

    def get_thread(self, thread_id: ThreadId) -> RawThreadSummary:
        response = self.__get_authenticated_thread_client() \
            .get(userId='me', id=thread_id) \
            .execute()
        return response

    def list_thread_ids(self, query: str | None = None) -> list[ThreadId]:
        """
        Get list of thread ids for a custom query, e.g. by date range. If more
        than one page is returned, this handels pagination under the hood.
        """
        all_thread_ids = []
        next_page_token = None
        while True:
            list_threads_response: RawThreadsList = self._list_thread_ids_paginated(
                next_page_token=next_page_token, 
                query=query
            )

            # Only keep id of each thread (for retrieving thread details later)
            try:
                thread_ids = [
                    thread['id'] for thread in list_threads_response['threads']
                ]
            except AttributeError:
                thread_ids = []
            all_thread_ids.extend(thread_ids)
            next_page_token = list_threads_response.get('nextPageToken')

            # Exit loop once no more pages are left
            if not next_page_token:
                return all_thread_ids

    def list_thread_ids_raw(
        self,
        query: str | None = None,
        next_page_token: NextPageToken | None = None,
    ) -> RawThreadsList:
        """
        Wrapper around Gmail API, returning response for listing thread ids for 
        a single page.
        """

        logger.info('Listing threadIDs for a single page.')        
        response =  self.__get_authenticated_thread_client() \
            .list(
                userId='me', 
                maxResults=500,
                includeSpamTrash=False, 
                q=query,
                pageToken=next_page_token, 
            ) \
            .execute()
        return response
                    
    def __get_authenticated_thread_client(self):
        gmail_client = self.core_client.get_authenticated_client()
        return gmail_client.users().threads()