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

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

import logging
from typing import ClassVar
import pydantic
import json
from datetime import datetime

from googleapiclient.discovery import Resource

from data_schemas.gmail.simple_types import ThreadId, NextPageToken
from data_schemas.gmail.get_thread import RawGmailThread
from data_schemas.gmail.list_threads import RawGmailThreadsList
from utils.dlq import DLQ
from .core_client import CoreClient


logger = logging.getLogger(__name__)


class ThreadClient:
    """
    API Documentation:
    https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.threads.html
    """

    _core_client: ClassVar = CoreClient()
    # Create separate DLQs for each type of API call, so we can keep messages
    # separate.
    _dlq_list_gmail_threads: ClassVar = DLQ(name='list_gmail_threads')
    _dlq_get_gmail_thread: ClassVar = DLQ(name='get_gmail_thread')


    def persist_DLQs(self) -> None:
        # todo: specify path to data directory
        self._dlq_list_gmail_threads.persist()
        self._dlq_get_gmail_thread.persist()


    def get_thread(self, thread_id: ThreadId) -> RawGmailThread | None:
        """
        Get details on a specific email thread, looked up by thread ID.

        This is a wrapper around the Gmail API. In addition, it performs schema
        validation on the response.

        Returns `None` if schema validation fails.
        Returns empty response if thread ID is not found.
        """

        response: dict = self.__get_authenticated_thread_client() \
            .get(  # pylint: disable='no-member'
                userId='me', id=thread_id
            ) \
            .execute()
        try:
            return RawGmailThread(**response)

        except pydantic.ValidationError as exception:
            msg = 'Could not convert get-thread response for thread-id ' \
                f'{thread_id} to RawGmailThread because it violated expected ' \
                'schema.'
            logger.warning(msg)

            self._dlq_get_gmail_thread.add_message(
                problem=msg,
                exception=exception,
                data=json.dumps(response)
            )
            return None

    def list_thread_ids(self, query: str | None = None) -> list[ThreadId]:
        """
        Get list of thread ids for a custom query, e.g. by date range.

        This function also handles:
          - pagination, if more than one page is returned.
          - schema validation on the response.
        """
        all_thread_ids: list[ThreadId] = []
        next_page_token: NextPageToken = None
        while True:
            list_threads_response: RawGmailThreadsList = \
                self._list_thread_ids_raw(
                    next_page_token=next_page_token,
                    query=query
                )

            # Only keep id of each thread (for retrieving thread details later)
            try:
                thread_ids: list[ThreadId] = [
                    thread.id for thread in list_threads_response.threads
                ]
            except AttributeError:
                thread_ids = []

            all_thread_ids.extend(thread_ids)
            next_page_token = list_threads_response.nextPageToken

            # Exit loop once no more pages are left
            if not next_page_token:
                return all_thread_ids

    def _list_thread_ids_raw(
        self,
        query: str | None = None,
        next_page_token: NextPageToken | None = None,
    ) -> RawGmailThreadsList | None:
        """
        Wrapper around Gmail API, returning response for listing thread ids for
        a single page. In addition, it performs schema validation on the
        response.
        """

        logger.info('Listing threadIDs for a single page.')
        response: dict = self.__get_authenticated_thread_client() \
            .list(  # pylint: disable='no-member'
                userId='me',
                maxResults=500,
                includeSpamTrash=False,
                q=query,
                pageToken=next_page_token,
        ) \
            .execute()

        try:
            return RawGmailThreadsList(**response)

        except pydantic.ValidationError as exception:
            msg = 'Couldnt convert list-threads response to RawGmailThreadsList'
            logger.warning(msg)

            self._dlq_list_gmail_threads.add_message(
                problem=msg,
                exception=exception,
                data=json.dumps(response)
            )
            return None

    def __get_authenticated_thread_client(self) -> Resource:
        gmail_client: Resource = self._core_client.get_authenticated_client()
        threads_resource: Resource = gmail_client.users().threads()  # pylint: disable='no-member'
        return threads_resource
