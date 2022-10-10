# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from data_models.models import Message

MY_EMAIL_ADDRESS = 'thomas.loeber73@gmail.com'

class EmailThread:
    def __init__(self, thread_id: str, messages: list[Message]):
        self.thread_id = thread_id
        
        # Store msg ids and senders as list for easier processing later
        self.msg_ids = [msg.msg_id for msg in messages]
        self.senders = [msg.sender for msg in messages]

        # Already compute this crucial field we always need twice
        self.index_of_first_msg_replied_to = \
            self._find_index_of_first_msg_replied_to()

    def _find_index_of_first_msg_replied_to(self) -> int:
        try:
            index_of_my_reply = self.senders.index(MY_EMAIL_ADDRESS)
            
        # If my email is not in the thread, there is no msg eliciting my reply
        except ValueError:
            index_of_first_msg_replied_to = None

        # This gets executed if no ValueError was raised:
        else:
            # If I initiated the thread, there is no msg eliciting the reply
            if index_of_my_reply == 0:
                index_of_first_msg_replied_to = None
            
            # Otherwise, return previous index
            index_of_first_msg_replied_to = index_of_my_reply - 1

        # This gets executed in any case
        finally:
            # Save result since we'll need to use it twice
            self.index_of_first_msg_replied_to = None 
            return index_of_first_msg_replied_to
            

    def find_msg_replied_to(self) -> str:
        """Returns id"""
        return self.msg_ids[self.index_of_first_msg_replied_to]


    def find_messages_to_discard(self) -> list[str]:
        """We need to discard any messages after the one eliciting reply."""
        # No need to worry about out-of-range index because there is always
        # at least the reply.
        index_of_first_msg_to_discard = self.index_of_first_msg_replied_to + 1
        return self.msg_ids[index_of_first_msg_to_discard: ]
