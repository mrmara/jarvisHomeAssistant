from typing import List, Tuple
from threading import Lock
from enum import Enum
import typing
if typing.TYPE_CHECKING:
    import include.basic_doer as basic_doer
class interrupt_status(Enum):
    COMPLETED = 1 # The item has completed its job and can be safely removed from the poll list
    POLLME = 2 # The item needs to be polled
    WORKING = 3 # The item is working, it is not ready to be polled
    POLLED = 4 # The item has been polled and its status has not been updated yet
    CONVERSATION = 5 # The item is in a conversation, poller is not allowed to poll anything else
    UNKNOWN = 6 # The item has an unknown status
class add_to_poll_return_status(Enum):
    ADDED = 1
    UPDATED = 2
    NOT_ADDED = 3
    
poll_list_mutex = Lock()
poll_list: List[Tuple['basic_doer.Doer', interrupt_status]] = []
'''
[THREAD SAFE]
Update the status of the item in the poll list
'''
def update_poll_list(item: 'basic_doer.Doer', status: interrupt_status) -> bool:
    poll_list_mutex.acquire()
    for i in range(0, len(poll_list)):
        if (poll_list[i][0] == item):
            poll_list[i][1] = status
            poll_list_mutex.release()
            return True
    poll_list_mutex.release()
    return False
'''
[THREAD SAFE]
Check if the item is in the poll list, if not add it, if it is, update its status.
It returns an add_to_poll_return_status enum
'''
def add_to_poll_list(item: 'basic_doer.Doer', status=interrupt_status.UNKNOWN) -> add_to_poll_return_status:
    
    if (update_poll_list(item, status)):
        return add_to_poll_return_status.UPDATED
    else:
        poll_list_mutex.acquire()
        poll_list.append([item, status])
        poll_list_mutex.release()
        return add_to_poll_return_status.ADDED
'''
[THREAD SAFE]
Remove the item from the poll list
'''
def remove_from_poll_list(item: 'basic_doer.Doer'):
    poll_list_mutex.acquire()
    for i in range(0, len(poll_list)):
        if (poll_list[i][0] == item):
            poll_list.pop(i)
            poll_list_mutex.release()
            return
    poll_list_mutex.release()
    return

def get_poll_status(item: 'basic_doer.Doer') -> interrupt_status:
    poll_list_mutex.acquire()
    for i in range(0, len(poll_list)):
        if (poll_list[i][0] == item):
            poll_list_mutex.release()
            return poll_list[i][1]
    poll_list_mutex.release()
    return interrupt_status.UNKNOWN