# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from data_models import MessageId, Message, ThreadId

MY_EMAIL_ADDRESS = 'thomas.loeber73@gmail.com'  # Todo: Make env variable

class EmailThread:
    def __init__(self, thread_id: ThreadId, messages: list[Message]):
        self.thread_id = thread_id
        
        # Store msg ids and senders as list for easier processing later
        self.msg_ids = [msg.msg_id for msg in messages]
        self.senders = [msg.sender for msg in messages]

        # Already compute this crucial field we always need twice
        self.index_of_first_msg_replied_to = \
            self._find_index_of_first_msg_replied_to()

    def _find_index_of_first_msg_replied_to(self) -> int | None:
        """
        If no msg elicited reply, returns `None`.

        Note: The reason for having this separate method returning index is the
        result of an earlier architecture that used list.index(), before 
        realizing the need for full-text search. Consider refactoring to return
        msgs replied to and msgs to ignore directly. 
        """
        
        for i in range(len(self.senders)):
            # Need to do full text search because field can be of the form
            # `John Doe <john.doe@email.com>`
            if MY_EMAIL_ADDRESS in self.senders[i]:
                # If my email started the thread, ignore whole thread
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
        Enables discarding any messages after the one eliciting reply, so they
        don't distort our data. 
        Returns None if no msgs need to be dropped.
        """
        # If no msg elicited reply, don't discard any. (My own messages will be 
        # dropped in separate step.)
        # NOTE: `is None` is not redundant! Without it, the index value 0 is 
        # cast to boolean and evaluates to False, so function returns None!
        if self.index_of_first_msg_replied_to is None:
            return None
        
        else:
            # No need to worry about out-of-range index because there is always
            # at least the reply.        
            first_msg_to_discard = self.index_of_first_msg_replied_to + 1
            return self.msg_ids[first_msg_to_discard: ]
        
    
    def get_transformed_data() -> dict[dict] | None:
        """
        Returns the thread's data in format needed for further analysis:
        - Msg id serves as a key for each row, consisting of whether a message 
        elicited a reply, the sender, and the email body (text).
        - All messages in a thread after the initial reply are discarded.
        - ToDo: All messages by myself are discarded.
        """
        pass