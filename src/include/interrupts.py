from threading import Lock
from enum import Enum
class interrupt_status(Enum):
    COMPLETED = 1
    POLLME = 2
    WORKING = 3
    UNKNOWN = 4
class add_to_poll_return_status(Enum):
    ADDED = 1
    UPDATED = 2
    NOT_ADDED = 3
    
poll_list_mutex = Lock()
poll_list = []
'''
[THREAD SAFE]
Update the status of the item in the poll list
'''
def update_poll_list(item: object, status: interrupt_status):
    poll_list_mutex.acquire()
    for i in range(0, len(poll_list)):
        if (poll_list[i][0] == item):
            poll_list[i][1] = status
            poll_list_mutex.release()
            return
    poll_list_mutex.release()
    return
'''
[THREAD SAFE]
Check if the item is in the poll list, if not add it, if it is, update its status.
It returns an add_to_poll_return_status enum
'''
def add_to_poll_list(item: object, status=interrupt_status.UNKNOWN) -> add_to_poll_return_status:
    poll_list_mutex.acquire()
    for i in range(0, len(poll_list)):
        if (poll_list[i][0] == item):
            poll_list[i][1] = status
            poll_list_mutex.release()
            return add_to_poll_return_status.UPDATED
    poll_list.append([item, status])
    poll_list_mutex.release()
    return add_to_poll_return_status.ADDED
'''
[THREAD SAFE]
Remove the item from the poll list
'''
def remove_from_poll_list(item: object):
    poll_list_mutex.acquire()
    for i in range(0, len(poll_list)):
        if (poll_list[i][0] == item):
            poll_list.pop(i)
            poll_list_mutex.release()
            return
    poll_list_mutex.release()
    return