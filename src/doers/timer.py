import time
from word2number import w2n
from include.basic_doer import *
class TimerManager(Doer):

    def __init__(self, logger: logging.Logger):
        if not self.__class__._INITIALIZED:
            self.ongoing_timer = None  # Initialize ongoing_timer
            super().__init__(logger.getChild("timer_manager"))
            
    def do(self, speechTxt, client_topic):
        self.logger.debug("timer intent")
        self.logger.debug(speechTxt)
        self.set_poll_topic(client_topic)
        for i in range(0, len(speechTxt)):
                
                if speechTxt[i] == "remaining":
                    self.logger.debug("Remaining time")
                    if self.ongoing_timer is not None and not self.ongoing_timer.expired:
                        response = self.ongoing_timer.get_remaining_time_response()
                        self.set_poll_payload(response)
                    else:
                        self.set_poll_payload("There is not an active timer to retrieve the requested information, sir")
                    self.update_poll_status(interrupts.interrupt_status.POLLME)
                    
                elif speechTxt[i] == "cancel":
                    self.logger.debug("Cancel timer")
                    if self.ongoing_timer is not None:
                        response = self.ongoing_timer.cancel_timer()
                        self.set_poll_payload(response)
                    else:
                        self.set_poll_payload("There is not an active timer to cancel, sir")
                    self.update_poll_status(interrupts.interrupt_status.POLLME, exhausted=True)
                    
                elif self.ongoing_timer is None or self.ongoing_timer.expired:
                    self.logger.debug(f"Start timer") 
                    secs = 0
                    mins = 0
                    for i in range(0, len(speechTxt)):
                        try:
                            num = w2n.word_to_num(speechTxt[i])
                        except Exception as e:
                            continue 
                        self.logger.debug(f"Detected number: {num}")
                        if len(speechTxt) > i + 1:
                            if speechTxt[i + 1] in ["minutes", "minute"]:
                                mins = num
                            elif speechTxt[i + 1] in ["seconds", "second"]:
                                secs = num
                        else:
                            break
                    if secs != 0 or mins != 0:
                        self.ongoing_timer = Timer(self.logger, mins, secs, self.timer_finished, self)
                        self.set_poll_payload(f"Timer of {mins} minutes and {secs} seconds started, sir")
                        self.update_poll_status(interrupts.interrupt_status.POLLME)
                        break
                else:
                    self.logger.debug("Ongoing timer")
                    self.set_poll_payload("I am sorry, there is an ongoing timer, sir")
                    self.update_poll_status(interrupts.interrupt_status.POLLME)
                    
    def timer_finished(self, name):
        self.set_poll_payload(f'{name} timer finished, sir')
        self.update_poll_status(interrupts.interrupt_status.POLLME, exhausted=True)
                                  
class Timer():
    
    def __init__(self, logger: logging.Logger, mins, secs, callback, manager):
        self.callback = callback
        self.manager = manager
        self.logger = logger.getChild("lonely")
        self.my_name = {self.logger.name.split(".")[-1]}
        if (mins == -1):
            mins = 0
        if (secs == -1):
            secs = 0
        self.logger.info(f"Timer of {mins} minutes and {secs} seconds STARTED")
        self.total_secs = secs + mins*60
        self.expired = False
        x = Thread(target=self.start_timer)
        x.start()
    
    def start_timer(self):
        self.remaining_secs = self.total_secs
        self.stop_timer = False
        while (self.remaining_secs) and not self.stop_timer:
            time.sleep(1)
            self.remaining_secs -= 1
        self.expired = True
        if not self.stop_timer:
            self.callback(self.my_name)
    
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