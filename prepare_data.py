# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
import logging
import pickle 

from thread_api import list_all_thread_ids, assign_msg_labels

PERSIST_RESULTS = True
FILTER_QUERY = 'After:2022/01/01'

class Counter:
    def __init__(self):
        self.state = 0

    def increment(self):
        self.state += 1


def main():
    thread_ids = list_all_thread_ids(
        query=FILTER_QUERY
    )
    msgs_replied_to, msgs_to_discard, dlq = \
        assign_msg_labels(thread_ids=thread_ids)
    
    if PERSIST_RESULTS:
        with open('msgs_replied_to.pickle', 'wb') as f:
            pickle.dump(obj=msgs_replied_to, file=f)

        with open('msgs_to_discard.pickle', 'wb') as f:
            pickle.dump(obj=msgs_to_discard, file=f)
            
    print(
        len(msgs_replied_to),
        len(msgs_to_discard),
        dlq
    )

if __name__ == '__main__':
    main()