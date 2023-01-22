from threading import Lock
from enum import Enum
class interrupt_status(Enum):
    COMPLETED = 1
    POLLME = 2
    WORKING = 3
poll_list_mutex = Lock()
poll_list = []