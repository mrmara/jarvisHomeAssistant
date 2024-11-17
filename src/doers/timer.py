import time
import threading
import include.interrupts as interrupts
from word2number import w2n
import logging
class timer_manager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(timer_manager, cls).__new__(cls)
        else:
            cls._instance.process(args[0], args[1])
        return cls._instance

    def __init__(self, speechTxt, client_topic, logger: logging.Logger):
        if not hasattr(self, 'initialized'):  # Ensure __init__ runs only once
            self.logger = logger.getChild("timer_manager")
            self.my_name = {self.logger.name.split(".")[-1]}
            self.ongoing_timer = None  # Initialize ongoing_timer
            self.initialized = True  # Mark as initialized
            self.process(speechTxt, client_topic)
            self.poll_payload = ""
            
    def process(self, speechTxt, client_topic):
        self.logger.debug("timer intent")
        self.logger.debug(speechTxt)
        self.client_topic = client_topic
        for i in range(0, len(speechTxt)):
                
                if speechTxt[i] == "remaining":
                    if self.ongoing_timer is not None and self.ongoing_timer.expired:
                        response = self.ongoing_timer.get_remaining_time_response()
                        self.ongoing_timer.set_poll_payload(response)
                        interrupts.add_to_poll_list(self.ongoing_timer, interrupts.interrupt_status.POLLME)
                    else:
                        self.set_poll_payload("There is not an active timer, sir")
                        interrupts.add_to_poll_list(self, interrupts.interrupt_status.POLLME)

                elif speechTxt[i] == "cancel":
                    if self.ongoing_timer is not None:
                        response = self.ongoing_timer.cancel_timer()
                        self.ongoing_timer.set_poll_payload(response)
                        interrupts.add_to_poll_list(self.ongoing_timer, interrupts.interrupt_status.POLLME)
                    else:
                        self.set_poll_payload("There is not an active timer, sir")
                        interrupts.add_to_poll_list(self, interrupts.interrupt_status.POLLME)  
                    
                elif self.ongoing_timer is None or self.ongoing_timer.expired:    
                    secs = 0
                    mins = 0
                    for i in range(0, len(speechTxt)):
                        try:
                            num = w2n.word_to_num(speechTxt[i])
                        except Exception as e:
                            continue 
                        self.logger.debug(num)
                        if len(speechTxt) > i + 1:
                            if speechTxt[i + 1] in ["minutes", "minute"]:
                                mins = num
                            elif speechTxt[i + 1] in ["seconds", "second"]:
                                secs = num
                        else:
                            break
                    if secs != 0 or mins != 0:
                        self.ongoing_timer = timer(self.logger, mins, secs, client_topic)
                        self.ongoing_timer.set_poll_payload(f"Timer of {mins} minutes and {secs} seconds started, sir")
                        interrupts.poll_list.append([self.ongoing_timer, interrupts.interrupt_status.POLLME])
                    break
                else:
                    self.set_poll_payload("I am sorry, there is an ongoing timer, sir")
                    interrupts.add_to_poll_list(self, interrupts.interrupt_status.POLLME)
                    
    def poll_me(self):
        self.logger.info(f"Polled {self.my_name}, my payload is {self.poll_payload}")
        return {"topic" : self.client_topic, "response" : self.poll_payload}
    
    def set_poll_payload(self, payload):
        self.logger.debug(f"Poll payload set to {payload}")
        self.poll_payload = payload
                                  
class timer():
    
    def __init__(self, logger: logging.Logger, mins, secs, client_topic):
        self.logger = logger.getChild("lonely")
        self.my_name = {self.logger.name.split(".")[-1]}
        self.client_topic = client_topic
        if (mins == -1):
            mins = 0
        if (secs == -1):
            secs = 0
        self.logger.info(f"Timer of {mins} minutes and {secs} seconds STARTED")
        self.total_secs = secs + mins*60
        self.expired = False
        x = threading.Thread(target=self.start_timer)
        x.start()
    
    def start_timer(self):
        self.remaining_secs = self.total_secs
        self.stop_timer = False
        while (self.remaining_secs) and not self.stop_timer:
            time.sleep(1)
            self.remaining_secs -= 1
        self.set_poll_payload(f'{self.my_name} timer finished, sir')
        interrupts.add_to_poll_list(self, interrupts.interrupt_status.POLLME)
        self.expired = True
    
    def get_remaining_time(self):
        mins, secs = divmod(self.remaining_secs, 60)
        return [mins, secs]
    
    def get_remaining_time_response(self):
        remaining_time = self.get_remaining_time()
        response = f"{remaining_time[0]} minutes and {remaining_time[1]} seconds, sir"
        self.logger.debug(response)
        return response
    
    def cancel_timer(self):
        self.stop_timer = True
        self.expired = True
        response = f'{self.my_name} timer cancelled, sir'
        self.logger.debug(response)
        return response
        
    def poll_me(self):
        self.logger.info(f"Polled {self.my_name}, my payload is {self.poll_payload}")
        if self.stop_timer:
            interrupts.remove_from_poll_list(self)
        else:
            interrupts.update_poll_list(self, interrupts.interrupt_status.WORKING)
        return {"topic" : self.client_topic, "response" : self.poll_payload}
    
    def set_poll_payload(self, payload):
        self.logger.debug(f"Poll payload set to {payload}")
        self.poll_payload = payload