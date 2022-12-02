# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

import logging
from typing import Final, ClassVar

from gmail_client.thread_client import ThreadClient
from data_schemas.gmail.get_thread import (
    RawGmailThread, ThreadId
)
from data_schemas.interface import RawMessageInterface
from email_domain.message import Message
from utils.dlq import DLQ

MY_EMAIL_ADDRESS: Final[str] = 'thomas.loeber73@gmail.com'  # Todo: Make argument
logger = logging.getLogger(__name__)


class EmailThread:
    """Domain representation of an email thread."""

    dlq: ClassVar[DLQ] = DLQ(name='EmailThread')

    def __init__(
        self,
        thread_id: ThreadId,
        # Actual class of list elements depends on email API
        # Todo: Define supertype, so we can add more specific type annotation
        messages: list,
    ):
        self.thread_id: ThreadId = thread_id
        self.messages: list[Message] = messages


    @classmethod
    def from_gmail(
        cls, thread_id: ThreadId, thread_client: ThreadClient
    ) -> EmailThread | None:
        """
        Construct a thread object, abiding by our *general* domain model (as
        defined by EmailThread class), using input from a *particular* email
        API (namely GMail).
        """

        response: RawGmailThread | None = thread_client.get_thread(
            thread_id=thread_id
        )
        if response is None:
            return None

        msgs: list[Message] = []
        for raw_msg in response.messages:
            raw_msg: RawMessageInterface
            try:
                msg = Message.from_gmail(raw_msg=raw_msg)
                msgs.append(msg)

            # If validation fails, save to dead letter queue
            except Exception as exception:
                EmailThread.dlq.add_message(
                    problem='Creating EmailThread failed',
                    exception=exception,
                    data=raw_msg.json(),
                )

        thread = cls(
            thread_id=thread_id,
            messages=msgs,
        )
        return thread


    def _find_index_of_first_msg_replied_to(self) -> int | None:
        """If no msg elicited reply, returns `None`."""

        # Note: The reason for having this separate method returning index is
        # the result of an earlier architecture that used list.index(), before
        # realizing the need for full-text search.
        # ToDo: Refactor to return msgs replied to and msgs to ignore directly.

        for i in range(len(self.senders)):
            # Need to do full text search because field can be of the form
            # `John Doe <john.doe@email.com>`
            if MY_EMAIL_ADDRESS in self.senders[i]:
                # If my msg started the thread, we can ignore whole thread
                if i == 0:
                    return None
                # Otherwise, return the previous index
                else:
                    return i - 1

        # If my email is not found in thread, there is no msg eliciting reply
        self.index_of_first_msg_replied_to = None
        return None

    def find_msg_replied_to(self) -> MessageId | None:
        """
        Returns id of message eliciting reply, if there is one. Otherwise
        returns `None`.
        """
        # If no msg elicited reply, return None. Handle this when calling
        # this method. NOTE: `is None` is not redundant! Without it, the index
        # value 0 is cast to boolean and evaluates to False, so returns None!
        if self.index_of_first_msg_replied_to is None:
            return None

        else:
            return self.msg_ids[self.index_of_first_msg_replied_to]

    def find_messages_to_discard(self) -> list[MessageId] | None:
        """
        Enables discarding:
        - any messages after the one eliciting reply, so they don't distort our
         data.
        - sent messages .
        Returns None if no msgs need to be dropped.
        """
        # If no msg elicited reply, only need to drop sent messages (`outbox`).
        # NOTE: `is None` is not redundant! Without it, the index value 0 is
        # cast to boolean and evaluates to False, so function returns None!
        if self.index_of_first_msg_replied_to is None:
            sent_messages = [
                msg for msg in self.msg_ids if MY_EMAIL_ADDRESS in msg
            ]
            return sent_messages

        else:
            # No need to worry about out-of-range index because there is always
            # at least the reply.
            first_msg_to_discard = self.index_of_first_msg_replied_to + 1
            return self.msg_ids[first_msg_to_discard: ]

    # def get_transformed_data(self) -> dict | None:
    #     """
    #     Returns the thread's data in format needed for further analysis:
    #     - Msg id serves as a key for each row, consisting of whether a message
    #     elicited a reply, the sender, and the email body (text).
    #     - All messages in a thread after the initial reply are discarded.
    #     - ToDo: All messages by myself are discarded.
    #     """
    #     result = {}
    #     msg_replied_to = self.find_msg_replied_to()
    #     msgs_to_discard = self.find_messages_to_discard()

    #     for i in range(self.n_msgs):
    #         msg_id = self.msg_ids[i]

    #         # Skip messages to discard
    #         if (msgs_to_discard is not None) and (msg_id in msgs_to_discard):
    #             continue

    #         if msg_replied_to is not None:
    #             replied_to = (msg_id == msg_replied_to)
    #         # Handle case where no message received reply
    #         else:
    #             replied_to = False

    #         result[msg_id] = {
    #             'replied_to': replied_to,
    #             'sender': self.senders[i],
    #             'body': self.msg_body[i],
    #             'timestamp': self.timestamps[i],
    #         }
    #     return result
