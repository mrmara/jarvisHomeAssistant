import time
import threading
import include.interrupts as interrupts
class timer():
    def __init__(self, logger, mins, secs, client_topic):
        self.logger = logger
        if (mins == -1):
            mins = 0
        if (secs == -1):
            secs = 0
        self.logger.info(f"Timer of {mins} minutes and {secs} seconds STARTED")
        self.total_secs = secs + mins*60
        self.client_topic = client_topic
        x = threading.Thread(target=self.start_timer)
        x.start()
    
    def start_timer(self):
        self.remaining_secs = self.total_secs
        self.stop_timer = False
        while (self.remaining_secs) and not self.stop_timer:
            time.sleep(1)
            self.remaining_secs -= 1
        interrupts.poll_list_mutex.acquire()
        for item in interrupts.poll_list:
            if (item[0] == self):
                self.logger.info(f"asking for poll")
                item[1] = interrupts.interrupt_status.POLLME
                break
        interrupts.poll_list_mutex.release()
    
    def get_remaining_time(self):
        mins, secs = divmod(self.remaining_secs, 60)
        return [mins, secs]

    def cancel_timer(self):
        self.stop_timer = True
        
    def poll_me(self):
        self.logger.info(f"Timer FINISHED")
        interrupts.poll_list_mutex.acquire()
        for item in interrupts.poll_list:
            if (item[0] == self):
                self.logger.info(f"removing from poll list")
                interrupts.poll_list.remove(item)
        interrupts.poll_list_mutex.release()
        return {"topic" : self.client_topic, "response" : "Timer finished, sir"}