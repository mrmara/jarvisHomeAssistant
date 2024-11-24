from __future__ import annotations
from abc import ABCMeta, abstractmethod
from threading import Lock, Thread
import logging
import include.interrupts as interrupts

class Doer(metaclass=ABCMeta):

    _INSTANCE: Doer = None
    _lock: Lock = Lock()
    _INITIALIZED: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            with cls._lock:
                if cls._INSTANCE is None:
                    cls._INSTANCE = super(Doer, cls).__new__(cls)
        return cls._INSTANCE

    @abstractmethod
    def __init__(self, logger: logging.Logger):
        if not self.__class__._INITIALIZED:
            self.logger = logger
            self.__base_logger = self.logger.getChild("doer")
            self.__base_logger.info(f"Creating {self.__class__.__name__} instance")
            self.my_name = {self.logger.name.split(".")[-1]}
            interrupts.add_to_poll_list(self)
            self.__class__._INITIALIZED = True
    
    @abstractmethod
    def do(self, speechTxt: list, client_topic: str):
        ...
        
    def poll_me(self):
        self.__base_logger.info(f"Polled {self.my_name}, my payload is {self.__poll_payload}")
        if self.exhausted:
            self.update_poll_status(interrupts.interrupt_status.COMPLETED)
        else:
            self.update_poll_status(interrupts.interrupt_status.POLLED)
        return {"topic" : self.__poll_topic, "response" : self.__poll_payload}
    
    def set_poll_payload(self, payload):
        self.__base_logger.debug(f"Poll payload set to {payload}")
        self.__poll_payload = payload
        
    def get_poll_payload(self):
        return self.__poll_payload

    def set_poll_topic(self, topic):
        self.__base_logger.debug(f"Poll topic set to {topic}")
        self.__poll_topic = topic
    
    def get_poll_topic(self):
        return self.__poll_topic
    
    def update_poll_status(self, status: interrupts.interrupt_status, exhausted: bool = False):
        self.exhausted = exhausted
        if status == interrupts.interrupt_status.CONVERSATION:
            self.something_to_say = True
        interrupts.update_poll_list(self, status)
    
    def get_poll_status(self):
        return interrupts.get_poll_status(self)
    
    def listen(self):
        if self.something_to_say:
            self.something_to_say = False
            return {"topic" : self.__poll_topic, "response" : self.__poll_payload}
        else:
            return None